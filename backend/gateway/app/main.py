
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import Response
import httpx

from backend.shared.config import settings


# --------------------------------------------------
# MAIN API GATEWAY
# --------------------------------------------------

app = FastAPI(
    title="Distributed Video Processing Platform",
    description=(
        "Single API Gateway and Swagger documentation "
        "for all video processing microservices."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# MICROSERVICE CONFIGURATION
# --------------------------------------------------

SERVICE_URLS = {
    "upload": f"http://127.0.0.1:{settings.upload_service_port}",
    "metadata": f"http://127.0.0.1:{settings.metadata_service_port}",
    "orchestrator": f"http://127.0.0.1:{settings.orchestrator_service_port}",
    "thumbnail": f"http://127.0.0.1:{settings.thumbnail_service_port}",
    "delivery": f"http://127.0.0.1:{settings.delivery_service_port}",
}

SERVICE_LABELS = {
    "upload": "Upload Service",
    "metadata": "Metadata Service",
    "orchestrator": "Transcoding Orchestrator",
    "thumbnail": "Thumbnail Service",
    "delivery": "Media Delivery Service",
}


# --------------------------------------------------
# GATEWAY HEALTH
# --------------------------------------------------

@app.get("/health", tags=["Gateway"])
async def health():
    return {
        "service": "Distributed Video Processing Platform",
        "status": "healthy",
    }


# --------------------------------------------------
# CHECK MICROSERVICE STATUS
# --------------------------------------------------

@app.get("/services", tags=["Gateway"])
async def service_status():

    results = {}

    async with httpx.AsyncClient(timeout=3) as client:

        for name, url in SERVICE_URLS.items():

            try:
                response = await client.get(f"{url}/health")

                results[name] = (
                    "available"
                    if response.status_code == 200
                    else "unavailable"
                )

            except httpx.RequestError:
                results[name] = "unavailable"

    return results


# --------------------------------------------------
# API GATEWAY REQUEST PROXY
# --------------------------------------------------

@app.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
async def proxy_request(
    service: str,
    path: str,
    request: Request,
):

    if service not in SERVICE_URLS:
        raise HTTPException(
            status_code=404,
            detail="Service not found.",
        )

    body = await request.body()

    try:

        async with httpx.AsyncClient(timeout=600) as client:

            response = await client.request(
                method=request.method,
                url=f"{SERVICE_URLS[service]}/{path}",
                params=request.query_params,
                content=body,
                headers={
                    key: value
                    for key, value in request.headers.items()
                    if key.lower() not in {
                        "host",
                        "content-length",
                        "connection",
                    }
                },
            )

        excluded_headers = {
            "content-length",
            "transfer-encoding",
            "connection",
            "content-encoding",
        }

        headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in excluded_headers
        }

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=headers,
        )

    except httpx.RequestError as error:

        raise HTTPException(
            status_code=503,
            detail=f"{service} service is unavailable: {str(error)}",
        )


# --------------------------------------------------
# UPDATE OPENAPI COMPONENT REFERENCES
# --------------------------------------------------

def rename_component_refs(data, prefix):

    if isinstance(data, dict):

        updated = {}

        for key, value in data.items():

            if key == "$ref" and isinstance(value, str):

                if value.startswith("#/components/"):

                    parts = value.split("/")

                    if len(parts) == 4:
                        value = (
                            f"#/components/{parts[2]}/"
                            f"{prefix}_{parts[3]}"
                        )

            updated[key] = rename_component_refs(value, prefix)

        return updated

    if isinstance(data, list):

        return [
            rename_component_refs(item, prefix)
            for item in data
        ]

    return data


# --------------------------------------------------
# COMBINED SWAGGER DOCUMENTATION
# --------------------------------------------------

def combined_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    combined_paths = dict(schema.get("paths", {}))

    components = schema.setdefault("components", {})

    combined_tags = list(schema.get("tags", []))

    with httpx.Client(timeout=10) as client:

        for service, base_url in SERVICE_URLS.items():

            prefix = service
            label = SERVICE_LABELS[service]

            try:

                response = client.get(
                    f"{base_url}/openapi.json"
                )

                response.raise_for_status()

                remote_schema = response.json()

                remote_paths = remote_schema.get(
                    "paths", {}
                )

                for path, path_item in remote_paths.items():

                    new_path = f"/{prefix}{path}"

                    updated_item = rename_component_refs(
                        path_item,
                        prefix,
                    )

                    for method, operation in updated_item.items():

                        if isinstance(operation, dict):

                            old_tags = operation.get("tags", [])

                            operation["tags"] = [
                                f"{label} - {tag}"
                                for tag in old_tags
                            ] or [label]

                            if operation.get("operationId"):

                                operation["operationId"] = (
                                    f"{prefix}_"
                                    f"{operation['operationId']}"
                                )

                    combined_paths[new_path] = updated_item

                remote_components = remote_schema.get(
                    "components", {}
                )

                for category, items in remote_components.items():

                    target = components.setdefault(
                        category, {}
                    )

                    for name, item in items.items():

                        new_name = f"{prefix}_{name}"

                        target[new_name] = rename_component_refs(
                            item,
                            prefix,
                        )

                combined_tags.append({
                    "name": label,
                    "description": (
                        f"API endpoints provided by {label}."
                    ),
                })

                print(
                    f"Successfully added {label} to Swagger."
                )

            except (
                httpx.HTTPError,
                ValueError,
                KeyError,
            ) as error:

                print(
                    f"Could not load {label} OpenAPI document: {error}"
                )

    schema["paths"] = combined_paths
    schema["tags"] = combined_tags

    app.openapi_schema = schema

    return app.openapi_schema


# --------------------------------------------------
# USE COMBINED OPENAPI GENERATOR
# --------------------------------------------------

app.openapi = combined_openapi
