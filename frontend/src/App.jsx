import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [inputUrl, setInputUrl] = useState('');
  const [summary, setSummary] = useState('');

  const handleInputChange = (event) => {
    setInputUrl(event.target.value);
  };

  const handleExtractClick = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/extract', { url: inputUrl }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      setSummary(response.data.summary);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <h2>Generate summary here</h2>
      <input
        type="text"
        placeholder="Enter YouTube video link"
        value={inputUrl}
        onChange={handleInputChange}
      />
      <button onClick={handleExtractClick}>Extract Summary</button>
      {summary && <p>{summary}</p>}
    </div>
  );
}

export default App;
