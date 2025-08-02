import React, { useEffect, useState } from "react";
import axios from "axios";

function Lessons() {
  const [data, setData] = useState([]);
  const [wikiSummary, setWikiSummary] = useState("");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState("");
  const [modalSubject, setModalSubject] = useState("");
  const [subjectFilter, setSubjectFilter] = useState("All");
  const [search, setSearch] = useState("");

  useEffect(() => {
    axios.get("http://localhost:5000/api/course-data")
      .then((res) => {
        console.log("✅ Fetched live course data:", res.data);
        setData(res.data);
      })
      .catch((err) => {
        console.error("❌ Error fetching live course data:", err);
      });
  }, []);

  const fetchWikiSummary = async (title, subject) => {
    setModalTitle(title);
    setModalSubject(subject);
    setModalOpen(true);
    setWikiSummary("Loading Wikipedia summary...");
    setYoutubeUrl("");
    try {
      const res = await axios.get(
        `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`
      );
      setWikiSummary(res.data.extract);
    } catch {
      setWikiSummary("No Wikipedia summary found.");
    }
    const searchUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(title + " tutorial")}`;
    setYoutubeUrl(searchUrl);
    try {
      await axios.post("http://localhost:5000/api/progress", {
        subject,
        title,
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      console.error("❌ Error logging progress:", err);
    }
  };

  // Get unique subjects for filter dropdown
  const subjects = ["All", ...Array.from(new Set(data.map(s => s.subject)))];

  // Filtered data based on subject and search
  const filteredData = data
    .filter(subject => subjectFilter === "All" || subject.subject === subjectFilter)
    .map(subject => ({
      ...subject,
      topics: (subject.topics || []).filter(topic =>
        topic.title.toLowerCase().includes(search.toLowerCase())
      )
    }))
    .filter(subject => subject.topics.length > 0);

  return (
    <div style={{ padding: "24px", maxWidth: 1400, margin: "0 auto" }}>
      <h2 style={{ textAlign: "center", marginBottom: 32 }}>📚 Educational Content</h2>
      {/* Filters */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 32, justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }}>
        <select
          value={subjectFilter}
          onChange={e => setSubjectFilter(e.target.value)}
          style={{ padding: '8px 16px', borderRadius: 8, border: '1px solid #bbb', fontSize: 16 }}
        >
          {subjects.map(subj => (
            <option key={subj} value={subj}>{subj}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Search topics..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ padding: '8px 16px', borderRadius: 8, border: '1px solid #bbb', fontSize: 16, minWidth: 220 }}
        />
      </div>
      {filteredData.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#888', fontSize: 18, marginTop: 40 }}>
          No topics found. Try a different subject or search term.
        </div>
      ) : (
        <div className="subjects-grid-4">
          {filteredData.map((subject, i) => (
            <div
              key={i}
              style={{
                background: "#f7f8fa",
                borderRadius: 16,
                boxShadow: "0 2px 12px rgba(0,0,0,0.07)",
                padding: 24,
                minHeight: 220,
                display: "flex",
                flexDirection: "column",
                justifyContent: "flex-start",
                borderTop: `6px solid #${((i * 1234567) % 0xffffff).toString(16).padStart(6, "0")}`,
              }}
            >
              <h3 style={{ color: "#2a2a5a", marginBottom: 12 }}>{subject.subject || "Unnamed Subject"}</h3>
              <div style={{ color: '#888', fontSize: 14, marginBottom: 8 }}>
                {subject.topics.length} topic{subject.topics.length !== 1 ? 's' : ''}
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                {(subject.topics || []).map((topic, j) => (
                  <div
                    key={j}
                    onClick={() => fetchWikiSummary(topic.title, subject.subject)}
                    style={{
                      background: "#e3e9ff",
                      color: "#1a237e",
                      borderRadius: 20,
                      padding: "6px 16px",
                      marginBottom: 6,
                      cursor: "pointer",
                      fontWeight: 500,
                      fontSize: 15,
                      boxShadow: "0 1px 4px rgba(60,60,120,0.07)",
                      transition: "background 0.2s, color 0.2s",
                    }}
                    onMouseOver={e => e.currentTarget.style.background = '#c7d2fe'}
                    onMouseOut={e => e.currentTarget.style.background = '#e3e9ff'}
                  >
                    {topic.title || "Untitled Topic"}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for Wikipedia summary and YouTube */}
      {modalOpen && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          background: "rgba(0,0,0,0.25)",
          zIndex: 1000,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
          onClick={() => setModalOpen(false)}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: 16,
              padding: 32,
              minWidth: 340,
              maxWidth: 500,
              boxShadow: "0 4px 32px rgba(0,0,0,0.18)",
              position: "relative",
            }}
            onClick={e => e.stopPropagation()}
          >
            <button
              onClick={() => setModalOpen(false)}
              style={{
                position: "absolute",
                top: 16,
                right: 16,
                background: "#f2f2f2",
                border: "none",
                borderRadius: 8,
                padding: "4px 10px",
                cursor: "pointer",
                fontWeight: 700,
                fontSize: 18,
              }}
              aria-label="Close"
            >
              ×
            </button>
            <h3 style={{ color: "#2a2a5a", marginBottom: 8 }}>{modalTitle}</h3>
            <div style={{ color: "#4a4e69", marginBottom: 12, fontSize: 15, fontWeight: 500 }}>{modalSubject}</div>
            <div style={{ marginBottom: 18, fontSize: 16 }}>{wikiSummary}</div>
            <a
              href={youtubeUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "inline-block",
                background: "#e3e9ff",
                color: "#1a237e",
                borderRadius: 8,
                padding: "8px 18px",
                fontWeight: 600,
                textDecoration: "none",
                marginTop: 8,
                transition: "background 0.2s, color 0.2s",
              }}
              onMouseOver={e => e.currentTarget.style.background = '#c7d2fe'}
              onMouseOut={e => e.currentTarget.style.background = '#e3e9ff'}
            >
              🎥 YouTube Tutorials
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

export default Lessons;
