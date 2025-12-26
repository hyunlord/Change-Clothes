'use client';

import { useState } from 'react';

export default function Home() {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [personImage, setPersonImage] = useState<File | null>(null);
  const [garmentImage, setGarmentImage] = useState<File | null>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleTryOn = async () => {
    if (!personImage || !garmentImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('person_image', personImage);
    formData.append('garment_image', garmentImage);
    formData.append('category', 'upper_body');

    try {
      // Remove trailing slash if present
      const baseUrl = apiUrl.replace(/\/$/, '');
      const response = await fetch(`${baseUrl}/try-on/image`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.result_image) {
        // Assuming backend returns a relative path like 'uploads/...'
        setResultImage(`${baseUrl}/${data.result_image}`);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to process try-on request. Check the API URL.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gray-900 text-white">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Virtual Try-On Service
        </h1>
        <div className="flex items-center gap-2 bg-gray-800 p-2 rounded-lg border border-gray-700">
          <span className="text-gray-400">API URL:</span>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-white w-64"
            placeholder="http://localhost:8000 or ngrok url"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl">
        {/* Person Image Input */}
        <div className="flex flex-col items-center gap-4 p-6 border border-gray-700 rounded-xl bg-gray-800/50">
          <h2 className="text-xl font-semibold">1. Person</h2>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setPersonImage(e.target.files?.[0] || null)}
            className="block w-full text-sm text-slate-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-violet-50 file:text-violet-700
              hover:file:bg-violet-100"
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

        {/* Garment Image Input */}
        <div className="flex flex-col items-center gap-4 p-6 border border-gray-700 rounded-xl bg-gray-800/50">
          <h2 className="text-xl font-semibold">2. Garment</h2>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setGarmentImage(e.target.files?.[0] || null)}
            className="block w-full text-sm text-slate-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-pink-50 file:text-pink-700
              hover:file:bg-pink-100"
          />
          {garmentImage && (
            <div className="relative w-full aspect-[3/4] bg-gray-700 rounded-lg overflow-hidden">
              <img
                src={URL.createObjectURL(garmentImage)}
                alt="Garment"
                className="object-cover w-full h-full"
              />
            </div>
          )}
        </div>

        {/* Result Output */}
        <div className="flex flex-col items-center gap-4 p-6 border border-gray-700 rounded-xl bg-gray-800/50">
          <h2 className="text-xl font-semibold">3. Result</h2>
          <div className="flex-1 flex items-center justify-center w-full">
            {loading ? (
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            ) : resultImage ? (
              <div className="relative w-full aspect-[3/4] bg-gray-700 rounded-lg overflow-hidden">
                <img
                  src={resultImage}
                  alt="Result"
                  className="object-cover w-full h-full"
                />
              </div>
            ) : (
              <div className="text-gray-500">Result will appear here</div>
            )}
          </div>
        </div>
      </div>

      <button
        onClick={handleTryOn}
        disabled={!personImage || !garmentImage || loading}
        className={`mt-12 px-8 py-4 rounded-full text-xl font-bold transition-all transform hover:scale-105
          ${(!personImage || !garmentImage || loading)
            ? 'bg-gray-600 cursor-not-allowed opacity-50'
            : 'bg-gradient-to-r from-violet-600 to-pink-600 hover:shadow-lg hover:shadow-purple-500/30'
          }`}
      >
        {loading ? 'Processing...' : 'Generate Try-On'}
      </button>
    </main>
  );
}
