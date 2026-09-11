import React from 'react';
import ResultsHeader from './ResultsHeader';
import StrategySummary from './StrategySummary';
import ContentCalendar from './ContentCalendar';

function ResultsDashboard({
  generatedContent,
  referenceFileCount = 0,
  onEditInputs,
  onResetPlan,
  onRegeneratePost,
  regeneratingPostNumber,
  onExportCSV
}) {
  if (!generatedContent) return null;

  return (
    <div className="results-dashboard-wrapper">
      <ResultsHeader
        generatedContent={generatedContent}
        referenceFileCount={referenceFileCount}
        onEditInputs={onEditInputs}
        onResetPlan={onResetPlan}
        onExportCSV={onExportCSV}
      />

      <StrategySummary strategy={generatedContent.content_strategy} />

      <ContentCalendar
        posts={generatedContent.posts}
        onRegeneratePost={onRegeneratePost}
        regeneratingPostNumber={regeneratingPostNumber}
      />
    </div>
  );
}

export default ResultsDashboard;
