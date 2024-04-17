import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [inputUrl, setInputUrl] = useState('');
  const [summary, setSummary] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Added state for loading

  const handleInputChange = (event) => {
    setInputUrl(event.target.value);
  };

  const handleExtractClick = async () => {
    setIsLoading(true); // Set loading to true before API call
    try {
      const response = await axios.post('http://127.0.0.1:8000/extract', { url: inputUrl }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      setSummary(response.data.summary);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false); // Set loading to false after API call (success or error)
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Generate summary here</h2>
      <input
        type="text"
        className="w-full border border-gray-300 rounded-md px-4 py-2 mb-4"
        placeholder="Enter YouTube video link"
        value={inputUrl}
        onChange={handleInputChange}
      />
      <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={handleExtractClick} disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Extract Summary'}
      </button>
      {summary && <p className="mt-4">{summary}</p>}
      {isLoading && (
        <div className="mt-4">
          {/* Add your loading animation component here */}
          <p>Fetching summary...</p>  {/* Example placeholder */}
        </div>
      )}
    </div>
  );
}

export default App;
