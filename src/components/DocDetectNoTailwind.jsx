import React, { useRef, useState, useEffect } from 'react'; 
import { useDropzone } from 'react-dropzone'; 
import axios from 'axios'; 
import * as pdfjsLib from "pdfjs-dist/webpack"; 
import './DocDetectNoTailwind.css'; 
 
const DEFAULT_API_URL = 'http://10.3.26.0:8000/api/inspect'; 
const RESULT_API_BASE = 'http://10.3.26.0:8000/api/result'; 
 
export default function DocDetectNoTailwind({ apiUrl = DEFAULT_API_URL }) { 
  const [file, setFile] = useState(null); 
  const [previewUrl, setPreviewUrl] = useState(null); 
  const [isPdf, setIsPdf] = useState(false); 
  const [loading, setLoading] = useState(false); 
  const [error, setError] = useState(null); 
  const [detections, setDetections] = useState([]); 
  const [resultImageUrl, setResultImageUrl] = useState(null); 
  const canvasRef = useRef(null); 
  const imgRef = useRef(null); 
  const origSize = useRef({ width: 0, height: 0 }); 
 
  const onDrop = (acceptedFiles) => { 
    const selectedFile = acceptedFiles[0]; 
    if (!selectedFile) return; 
    setFile(selectedFile); 
    setError(null); 
    setDetections([]); 
    setResultImageUrl(null); 
    const url = URL.createObjectURL(selectedFile); 
    setPreviewUrl(url); 
    setIsPdf(selectedFile.type === 'application/pdf' || 
selectedFile.name.toLowerCase().endsWith('.pdf')); 
  }; 
 
  const { getRootProps, getInputProps, isDragActive } = useDropzone({  
    onDrop,  
    multiple: false,  
    accept: { 'image/*': [], 'application/pdf': ['.pdf'] }  
  }); 
 
  useEffect(() => { 
    if (!previewUrl) return; 
    if (isPdf) renderPdfToCanvas(previewUrl); 
    else loadImage(previewUrl); 
    return () => {  
      try { URL.revokeObjectURL(previewUrl); } catch (e) {}  
    }; 
  }, [previewUrl, isPdf]); 
 
  function loadImage(url) { 
    const img = new Image(); 
    img.onload = () => { 
      origSize.current = { width: img.width, height: img.height }; 
      imgRef.current = img; 
      drawBaseImage(); 
    }; 
    img.onerror = () => setError('Не удалось загрузить изображение'); 
    img.src = url; 
  } 
 
  async function renderPdfToCanvas(url) { 
    try { 
      const pdf = await pdfjsLib.getDocument(url).promise; 
      const page = await pdf.getPage(1); 
      const scale = 1.5; 
      const viewport = page.getViewport({ scale }); 
      const canvas = canvasRef.current; 
      canvas.width = viewport.width; 
      canvas.height = viewport.height; 
      const ctx = canvas.getContext('2d'); 
      await page.render({ canvasContext: ctx, viewport }).promise; 
      origSize.current = { width: viewport.width, height: viewport.height }; 
    } catch (e) { 
      setError('Ошибка рендеринга PDF: ' + e.message); 
    } 
  } 
 
  function drawBaseImage() { 
    const canvas = canvasRef.current; 
    if (!canvas) return; 
    const ctx = canvas.getContext('2d'); 
    canvas.width = imgRef.current.width; 
    canvas.height = imgRef.current.height; 
    ctx.clearRect(0, 0, canvas.width, canvas.height); 
    ctx.drawImage(imgRef.current, 0, 0); 
  } 
 
  function drawDetections(list) { 
    const canvas = canvasRef.current; 
    if (!canvas) return; 
    const ctx = canvas.getContext('2d'); 
     
    ctx.lineWidth = 3; 
    list.forEach(d => { 
      const [x, y, w, h] = d.bbox; 
      ctx.strokeStyle = d.label === 'signature' ? '#059669' : '#1e40af'; 
      ctx.strokeRect(x, y, w, h); 
      ctx.font = '16px Arial'; 
      ctx.fillStyle = ctx.strokeStyle; 
      const text = `${d.label} ${Math.round(d.score * 100)}%`; 
      ctx.fillText(text, Math.max(6, x + 6), Math.max(18, y + 18)); 
    }); 
  } 
 
  useEffect(() => {  
    if (detections.length) drawDetections(detections);  
  }, [detections]); 
 
  async function handleSend() { 
    if (!file) return; 
    setError(null); 
    setLoading(true); 
    setDetections([]); 
    setResultImageUrl(null); 
 
    try { 
      const form = new FormData(); 
      form.append('file', file); 
       
      console.log('Sending to:', DEFAULT_API_URL); 
       
      const resp = await axios.post(DEFAULT_API_URL, form, {  
        headers: { 'Content-Type': 'multipart/form-data' },  
        timeout: 120000  
      }); 
 
      if (resp.data) {
       adaptAndSet(resp.data);
      }
    } catch (error) { 
      console.error('Error:', error); 
      setError('Ошибка запроса: ' + (error.response?.data?.message || error.message)); 
    } finally {  
      setLoading(false);  
    } 
  } 
 
  function adaptAndSet(data) { 
    const W = data.width || origSize.current.width || 1; 
    const H = data.height || origSize.current.height || 1; 
    const first = data.detections && data.detections[0]; 
    const normalized = first && Math.max(...first.bbox) <= 1; 
     
    const adapted = data.detections.map(d => { 
      if (normalized) { 
        const [nx, ny, nw, nh] = d.bbox; 
        return { ...d, bbox: [nx * W, ny * H, nw * W, nh * H] }; 
      } else { 
        return d; 
      } 
    }); 
     
    setDetections(adapted); 
  } 
 
  return ( 
    <div className="container"> 
      <div className="header"> 
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none"> 
          <rect x="2" y="2" width="20" height="20" rx="5" fill="#3b82f6" /> 
        </svg> 
        Проверка документа на подпись и штамп 
      </div> 
 
      <div {...getRootProps()} className="dropzone" role="button"> 
        <input {...getInputProps()} /> 
        <div> 
          {isDragActive ? 'Отпустите файл здесь...' : 'Перетащите PDF или изображение сюда'} 
        </div> 
      </div> 
 
      {previewUrl && ( 
        <div className="previewBox"> 
          <div className="canvasWrapper"> 
            <canvas ref={canvasRef} style={{ maxWidth: '100%', height: 'auto' }} /> 
          </div> 
        </div> 
      )} 
 
      <div className="controls"> 
        <button className="btn" onClick={handleSend} disabled={!file || loading}> 
          {loading ? 'Загрузка...' : 'Отправить'} 
        </button> 
        <button className="btn secondary" onClick={() => { 
          setFile(null); 
          setPreviewUrl(null); 
          setDetections([]); 
          setError(null); 
          setResultImageUrl(null); 
        }}> 
          Сбросить 
        </button> 
      </div> 
 
      {error && <div className="error">{error}</div>} 
 
      {detections.length > 0 && ( 
        <div className="results"> 
          <h3>Найденные объекты:</h3> 
          <ul className="list"> 
            {detections.map((d, i) => ( 
              <li key={i}> 
                <b>{d.label === 'signature' ? 'Подпись' : 'Штамп'}</b> — {Math.round(d.score * 
100)}%<br /> 
                bbox: {d.bbox.map(v => Math.round(v)).join(', ')} 
              </li> 
            ))} 
          </ul> 
        </div> 
      )} 
    </div> 
  ); 
} 

 