'use client';

import { useState } from 'react';

export default function Home() {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [personImage, setPersonImage] = useState<File | null>(null);
  const [modelType, setModelType] = useState('b2');

  // New State Structure
  const [analysisResult, setAnalysisResult] = useState<{
    body_parts: { label: string, url: string }[],
    clothing_items: { label: string, url: string }[],
  } | null>(null);

  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!personImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('person_image', personImage);
    formData.append('model_type', modelType);

    try {
      // Remove trailing slash if present
      const baseUrl = apiUrl.replace(/\/$/, '');
      const response = await fetch(`${baseUrl}/analyze`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      if (data.status === 'completed') {
        const attachBaseUrl = (items: any[]) => items.map(item => ({
          ...item,
          url: `${baseUrl}/${item.url}`
        }));

        setAnalysisResult({
          body_parts: attachBaseUrl(data.body_parts),
          clothing_items: attachBaseUrl(data.clothing_items),
        });
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to process analysis request. Check the API URL.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-900 text-white">
      <div className="z-10 max-w-6xl w-full items-center justify-between font-mono text-sm lg:flex mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Virtual Try-On: Image Analysis
        </h1>
        <div className="flex items-center gap-2 bg-gray-800 p-2 rounded-lg border border-gray-700">
          <span className="text-gray-400">API URL:</span>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-white w-64"
            placeholder="ngrok url"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full max-w-7xl">
        {/* Input Section */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold border-b border-gray-700 pb-2">1. Upload Person</h2>
          <div className="flex flex-col gap-4 bg-gray-800 p-6 rounded-xl border border-gray-700">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setPersonImage(e.target.files?.[0] || null)}
              className="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:bg-violet-900 file:text-violet-200 hover:file:bg-violet-800"
            />
            {personImage && (
              <div className="relative w-full aspect-[3/4] bg-gray-700 rounded-lg overflow-hidden">
                <img
                  src={URL.createObjectURL(personImage)}
                  alt="Person"
                  className="object-cover w-full h-full"
                />
              </div>
            )}
          </div>

          {/* Model Selection */}
          <div className="flex flex-col gap-4 bg-gray-800 p-6 rounded-xl border border-gray-700">
            <label className="text-lg font-semibold flex items-center gap-2">
              🧠 AI Model
            </label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              className="bg-gray-900 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-violet-500 outline-none"
            >
              <option value="b2">Segformer B2 (⚡ Fast)</option>
              <option value="b5">Segformer B5 (✨ High Quality)</option>
              <option value="sam">Segment Anything (SAM) (🧩 All Regions)</option>
            </select>
            <p className="text-xs text-gray-400">
              * B2/B5: Categorized (Clothes vs Body). SAM: All regions (Uncategorized).
            </p>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!personImage || loading}
            className={`w-full py-4 rounded-xl text-xl font-bold transition-all
                ${(!personImage || loading)
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-violet-600 to-pink-600 hover:shadow-lg hover:shadow-purple-500/30'
              }`}
          >
            {loading ? 'Analyzing...' : 'Analyze Image'}
          </button>
        </div>

        {/* Output Section */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold border-b border-gray-700 pb-2">2. Analysis Results</h2>

          {!analysisResult && !loading && (
            <div className="h-64 flex items-center justify-center text-gray-500 border-2 border-dashed border-gray-800 rounded-xl">
              Results will appear here
            </div>
          )}

          {loading && (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            </div>
          )}

          {analysisResult && (
            <div className="grid grid-cols-2 gap-6 animate-fade-in">
              {/* Body Parts */}
              <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                <h3 className="text-lg font-bold text-violet-300 mb-4 flex items-center gap-2">
                  <span>👤</span> Detected Body
                </h3>
                <div className="space-y-4">
                  {analysisResult.body_parts.length === 0 && <p className="text-gray-500 text-sm">No body parts detected</p>}
                  {analysisResult.body_parts.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-4 bg-gray-800 p-2 rounded-lg">
                      <div className="w-16 h-16 bg-gray-900 rounded overflow-hidden">
                        <img src={item.url} alt={item.label} className="object-contain w-full h-full" />
                      </div>
                      <span className="font-medium">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Clothing Items */}
              <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                <h3 className="text-lg font-bold text-pink-300 mb-4 flex items-center gap-2">
                  <span>👕</span> Detected Clothing
                </h3>
                <div className="space-y-4">
                  {analysisResult.clothing_items.length === 0 && <p className="text-gray-500 text-sm">No clothing detected</p>}
                  {analysisResult.clothing_items.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-4 bg-gray-800 p-2 rounded-lg">
                      <div className="w-16 h-16 bg-gray-900 rounded overflow-hidden">
                        <img src={item.url} alt={item.label} className="object-contain w-full h-full" />
                      </div>
                      <span className="font-medium">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

