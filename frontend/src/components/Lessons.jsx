import React, { useEffect, useState } from "react";
import axios from "axios";
import './Lessons.css';

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
            axios.get("https://ai-tutor-backend-m4rr.onrender.com/api/course-data")
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
              await axios.post("https://ai-tutor-backend-m4rr.onrender.com/api/progress", {
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
    <div className="lessons-container">
      <div className="lessons-header">
        <h2>📚 Educational Content</h2>
      </div>
      
      {/* Filters */}
      <div className="filters-container">
        <select
          value={subjectFilter}
          onChange={e => setSubjectFilter(e.target.value)}
          className="filter-select"
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
          className="search-input"
        />
      </div>
      
      {filteredData.length === 0 ? (
        <div className="no-topics-message">
          No topics found. Try a different subject or search term.
        </div>
      ) : (
        <div className="subjects-grid-4">
          {filteredData.map((subject, i) => (
            <div key={i} className="subject-card">
              <h3 className="subject-title">{subject.subject || "Unnamed Subject"}</h3>
              <div className="topic-count">
                {subject.topics.length} topic{subject.topics.length !== 1 ? 's' : ''}
              </div>
              <div className="topics-container">
                {(subject.topics || []).map((topic, j) => (
                  <button
                    key={j}
                    onClick={() => fetchWikiSummary(topic.title, subject.subject)}
                    className="topic-chip"
                  >
                    {topic.title || "Untitled Topic"}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for Wikipedia summary and YouTube */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button
              onClick={() => setModalOpen(false)}
              className="modal-close-button"
              aria-label="Close"
            >
              ×
            </button>
            <h3 className="modal-title">{modalTitle}</h3>
            <div className="modal-subject">{modalSubject}</div>
            <div className="modal-summary">{wikiSummary}</div>
            <a
              href={youtubeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="youtube-link"
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
