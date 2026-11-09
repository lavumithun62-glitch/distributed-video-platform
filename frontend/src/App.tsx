
import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8006";

type Video = {
  id: string;
  filename: string;
  status: string;
  size: string;
  resolutions: string[];
  thumbnail: string;
};

type Dashboard = {
  mode: string;
  total_videos: number;
  completed: number;
  processing: number;
  uploaded: number;
  videos: Video[];
  services: Record<string, string>;
};

export default function App() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}//dashboard`)
      .then((response) => {
        if (!response.ok) throw new Error("Backend request failed");
        return response.json();
      })
      .then(setData)
      .catch(() => setError("Cannot connect to  backend. Start port 8006."));
  }, []);

  if (error) {
    return <main className="page"><h2>Backend connection error</h2><p>{error}</p></main>;
  }

  if (!data) {
    return <main className="page"><h2>Loading dashboard...</h2></main>;
  }

  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>Distributed Video Processing Platform</h1>
          <p>Video Upload â€¢ Transcoding â€¢ Thumbnail Generation â€¢ Delivery</p>
        </div>
        <span className=""></span>
      </header>

      <section className="stats">
        <article className="stat"><span>Total Videos</span><strong>{data.total_videos}</strong></article>
        <article className="stat"><span>Completed</span><strong>{data.completed}</strong></article>
        <article className="stat"><span>Processing</span><strong>{data.processing}</strong></article>
        <article className="stat"><span>Uploaded</span><strong>{data.uploaded}</strong></article>
      </section>

      <section className="panel">
        <h2>Microservice Health</h2>
        <div className="services">
          {Object.entries(data.services).map(([name, status]) => (
            <div className="service" key={name}>
              <span className="dot" />
              <div><strong>{name}</strong><small>{status}</small></div>
            </div>
          ))}
        </div>
        <p className="note"> indicators only â€” these do not represent live microservice health.</p>
      </section>

      <section className="panel">
        <h2>Video Library</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Video ID</th><th>File Name</th><th>Size</th>
                <th>Status</th><th>Resolutions</th><th>Thumbnail</th>
              </tr>
            </thead>
            <tbody>
              {data.videos.map((video) => (
                <tr key={video.id}>
                  <td>{video.id}</td>
                  <td>{video.filename}</td>
                  <td>{video.size}</td>
                  <td><span className={`status ${video.status}`}>{video.status}</span></td>
                  <td>{video.resolutions.length ? video.resolutions.join(", ") : "â€”"}</td>
                  <td>{video.thumbnail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer>Distributed Video Processing Platform Â· Sample demonstration data</footer>
    </main>
  );
}

