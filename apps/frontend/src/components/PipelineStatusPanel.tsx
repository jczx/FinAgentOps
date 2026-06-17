import type { PipelineStatus } from "../data/dashboardMock";

type PipelineStatusPanelProps = {
	pipeline: PipelineStatus;
};

export function PipelineStatusPanel({ pipeline }: PipelineStatusPanelProps) {
	const progress = (pipeline.stepsCompleted / pipeline.totalSteps) * 100;

	return (
		<section
			className="panel pipeline-panel"
			id="pipeline"
			aria-labelledby="pipeline-heading"
		>
			<p className="eyebrow">Data engineering</p>
			<h2 id="pipeline-heading">Pipeline status</h2>
			<div className="status-row">
				<span>Status</span>
				<strong>{pipeline.status}</strong>
			</div>
			<div className="progress" aria-label={`Pipeline progress ${progress}%`}>
				<span style={{ width: `${progress}%` }} />
			</div>
			<p>
				{pipeline.stepsCompleted} of {pipeline.totalSteps} mock steps completed.
			</p>
			<small>Last run: {pipeline.lastRun}</small>
		</section>
	);
}
