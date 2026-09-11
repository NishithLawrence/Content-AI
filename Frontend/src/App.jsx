import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import IndustrySelector from './components/IndustrySelector';
import ContentPlanSelector from './components/ContentPlanSelector';
import PlatformSelector from './components/PlatformSelector';
import FileUploader from './components/FileUploader';
import GenerateButton from './components/GenerateButton';
import ResultsDashboard from './components/ResultsDashboard';
import Toast from './components/Toast';
import './App.css';

function App() {
  // Generator State management
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [selectedDuration, setSelectedDuration] = useState('');
  const [postCount, setPostCount] = useState(0);
  const [selectedPlatform, setSelectedPlatform] = useState('Instagram');
  const [referenceFiles, setReferenceFiles] = useState([]);
  
  // Results & View State
  const [generatedContent, setGeneratedContent] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [regeneratingPostNumber, setRegeneratingPostNumber] = useState(null);

  // Async & Progress state
  const [isGenerating, setIsGenerating] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [toastMessage, setToastMessage] = useState(null);

  const stageTimerRef = useRef(null);

  // Check backend health endpoint
  const checkHealth = async () => {
    try {
      const response = await fetch('/api/health');
      if (response.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('disconnected');
      }
    } catch {
      setBackendStatus('disconnected');
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Event handlers
  const handleSelectIndustry = (industryId) => {
    setSelectedIndustry(industryId);
  };

  const handleSelectPlan = (duration, count) => {
    setSelectedDuration(duration);
    setPostCount(count);
  };

  const handleSelectPlatform = (platformId) => {
    setSelectedPlatform(platformId);
  };

  const handleAddFiles = (newFiles) => {
    setReferenceFiles((prev) => [...prev, ...newFiles]);
  };

  const handleRemoveFile = (indexToRemove) => {
    setReferenceFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  const isFormValid = Boolean(selectedIndustry && selectedDuration && postCount > 0);

  const startProgressStages = (hasFiles) => {
    const stages = hasFiles ? [
      "Reading your reference material...",
      "Understanding your brand...",
      "Planning your content calendar...",
      "Writing industry-specific posts...",
      "Finalizing your content plan..."
    ] : [
      "Understanding your brand...",
      "Planning your content calendar...",
      "Writing industry-specific posts...",
      "Finalizing your content plan..."
    ];

    let currentIdx = 0;
    setLoadingStage(stages[0]);

    if (stageTimerRef.current) clearInterval(stageTimerRef.current);

    stageTimerRef.current = setInterval(() => {
      currentIdx++;
      if (currentIdx < stages.length) {
        setLoadingStage(stages[currentIdx]);
      } else {
        clearInterval(stageTimerRef.current);
      }
    }, 1800);
  };

  const stopProgressStages = () => {
    if (stageTimerRef.current) {
      clearInterval(stageTimerRef.current);
      stageTimerRef.current = null;
    }
    setLoadingStage('');
  };

  const handleGenerate = async () => {
    if (!isFormValid || isGenerating) return;

    setIsGenerating(true);
    const hasFiles = referenceFiles.length > 0;
    startProgressStages(hasFiles);

    try {
      const formData = new FormData();
      formData.append('industry', selectedIndustry);
      formData.append('duration', selectedDuration);
      formData.append('post_count', postCount);
      formData.append('platform', selectedPlatform);

      referenceFiles.forEach((file) => {
        formData.append('files', file);
      });

      const response = await fetch('/api/generate-content', {
        method: 'POST',
        body: formData,
      });

      const responseText = await response.text();
      let data = null;

      if (responseText && responseText.trim().length > 0) {
        try {
          data = JSON.parse(responseText);
        } catch {
          data = null;
        }
      }

      if (!response.ok) {
        const errorDetail = data?.detail || data?.message || (responseText && !responseText.trim().startsWith('<') ? responseText.slice(0, 200) : null);
        if (errorDetail) {
          throw new Error(errorDetail);
        } else {
          throw new Error('Unable to reach the AI service. Please make sure the backend is running and try again.');
        }
      }

      if (!data) {
        throw new Error('Unable to reach the AI service. Please make sure the backend is running and try again.');
      }

      console.log('Successfully generated content plan:', data);
      setGeneratedContent(data);
      setShowResults(true);
      setToastMessage(`✨ Content Plan Ready! Generated ${data.total_posts} posts for ${data.industry}.`);
    } catch (err) {
      console.error('Error generating content:', err);
      const isConnectionOrSyntaxErr =
        !err.message ||
        err.message.includes('Unexpected end of JSON input') ||
        err.message.includes('Failed to fetch') ||
        err.message.includes('JSON.parse');

      const userMessage = isConnectionOrSyntaxErr
        ? 'Unable to reach the AI service. Please make sure the backend is running and try again.'
        : err.message;

      setToastMessage(`❌ Error: ${userMessage}`);
    } finally {
      stopProgressStages();
      setIsGenerating(false);
    }
  };

  const handleEditInputs = () => {
    setShowResults(false);
  };

  const handleResetPlan = () => {
    setGeneratedContent(null);
    setShowResults(false);
  };

  const handleRegenerateSinglePost = async (post) => {
    if (regeneratingPostNumber) return;

    setRegeneratingPostNumber(post.post_number);
    try {
      const response = await fetch('/api/regenerate-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          industry: selectedIndustry,
          platform: selectedPlatform,
          duration: selectedDuration,
          post_number: post.post_number,
          day: post.day,
          content_pillar: post.content_pillar,
          reference_context: referenceFiles.length > 0 ? `Reference file count: ${referenceFiles.length}` : '',
          original_caption: post.caption
        })
      });

      const updatedPost = await response.json();
      if (!response.ok) {
        throw new Error(updatedPost.detail || 'Failed to regenerate post.');
      }

      setGeneratedContent((prev) => ({
        ...prev,
        posts: prev.posts.map((p) => (p.post_number === post.post_number ? updatedPost : p))
      }));
      setToastMessage(`✨ Post ${post.post_number} regenerated successfully!`);
    } catch (err) {
      setToastMessage(`❌ Error: ${err.message}`);
    } finally {
      setRegeneratingPostNumber(null);
    }
  };

  const handleExportCSV = () => {
    if (!generatedContent) return;

    const { industry, duration, platform, posts } = generatedContent;
    let csv = `Post Number,Day,Content Pillar,Caption,Visual Direction,Hashtags\n`;

    posts.forEach((p) => {
      const cleanCaption = `"${p.caption.replace(/"/g, '""')}"`;
      const cleanVisual = `"${p.visual_direction.replace(/"/g, '""')}"`;
      const cleanTags = `"${p.hashtags.join(' ').replace(/"/g, '""')}"`;
      csv += `${p.post_number},"${p.day}","${p.content_pillar}",${cleanCaption},${cleanVisual},${cleanTags}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `content-plan-${industry.toLowerCase().replace(/[^a-z0-9]/g, '-')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setToastMessage('📥 Content Plan exported as CSV!');
  };

  return (
    <div className="saas-app">
      <Header backendStatus={backendStatus} />

      <main className="main-content-wrapper">
        {!showResults ? (
          <>
            <HeroSection />

            <div className="generator-dashboard">
              <IndustrySelector
                selectedIndustry={selectedIndustry}
                onSelectIndustry={handleSelectIndustry}
              />

              <ContentPlanSelector
                selectedDuration={selectedDuration}
                onSelectPlan={handleSelectPlan}
              />

              <PlatformSelector
                selectedPlatform={selectedPlatform}
                onSelectPlatform={handleSelectPlatform}
              />

              <FileUploader
                files={referenceFiles}
                onAddFiles={handleAddFiles}
                onRemoveFile={handleRemoveFile}
              />

              <GenerateButton
                isFormValid={isFormValid}
                isGenerating={isGenerating}
                loadingStage={loadingStage}
                onGenerate={handleGenerate}
                selectedIndustry={selectedIndustry}
                selectedDuration={selectedDuration}
              />
            </div>
          </>
        ) : (
          <ResultsDashboard
            generatedContent={generatedContent}
            referenceFileCount={referenceFiles.length}
            onEditInputs={handleEditInputs}
            onResetPlan={handleResetPlan}
            onRegeneratePost={handleRegenerateSinglePost}
            regeneratingPostNumber={regeneratingPostNumber}
            onExportCSV={handleExportCSV}
          />
        )}
      </main>

      <footer className="saas-footer">
        <span>ContentAI Studio • SaaS Platform v1.0</span>
      </footer>

      {toastMessage && (
        <Toast
          message={toastMessage}
          onClose={() => setToastMessage(null)}
        />
      )}
    </div>
  );
}

export default App;
