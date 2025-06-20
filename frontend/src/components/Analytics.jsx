import React, { useEffect, useState } from "react";
import axios from "axios";

function Analytics() {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:5000/api/analytics").then((res) => {
      setAnalytics(res.data);
    });
  }, []);

  if (!analytics) return <p>Loading analytics...</p>;

  return (
    <div style={{ padding: "20px" }}>
      <h2>📊 Analytics</h2>
      <p>Total Views: {analytics.total_views}</p>

      <h3>Views by Subject:</h3>
      <ul>
        {Object.entries(analytics.views_by_subject).map(([subject, count]) => (
          <li key={subject}>
            {subject}: {count}
          </li>
        ))}
      </ul>

      <h3>Views by Topic:</h3>
      <ul>
        {Object.entries(analytics.views_by_topic).map(([title, count]) => (
          <li key={title}>
            {title}: {count}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Analytics;
