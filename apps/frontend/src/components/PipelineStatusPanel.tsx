import type { PipelineStatus } from "../data/dashboardTypes";

type PipelineStatusPanelProps = {
	pipeline: PipelineStatus;
};

function formatDate(value: string | null): string {
	if (!value) {
		return "Not available";
	}

	return new Intl.DateTimeFormat("en-US", {
		dateStyle: "medium",
		timeStyle: "short",
	}).format(new Date(value));
}

export function PipelineStatusPanel({ pipeline }: PipelineStatusPanelProps) {
	const progress =
		pipeline.totalSteps > 0
			? (pipeline.stepsCompleted / pipeline.totalSteps) * 100
			: 0;

	return (
		<section
			className="panel pipeline-panel"
			id="pipeline"
			aria-labelledby="pipeline-heading"
		>
			<p className="eyebrow">Data engineering</p>
			<h2 id="pipeline-heading">Pipeline status</h2>
			<div className="status-row">
				<span>Latest status</span>
				<strong>{pipeline.status}</strong>
			</div>
			<div className="progress" aria-label={`Pipeline progress ${progress}%`}>
				<span style={{ width: `${progress}%` }} />
			</div>
			<p>{pipeline.message}</p>
			<small>Last run: {formatDate(pipeline.lastRun)}</small>

			<div className="pipeline-runs" aria-label="Latest pipeline runs">
				{pipeline.runs.slice(0, 5).map((run) => (
					<article className="pipeline-run" key={`${run.sourceName}-${run.startedAt}`}>
						<div>
							<strong>{run.sourceName}</strong>
							<span>{run.status}</span>
						</div>
						<p>{run.recordsProcessed.toLocaleString()} records processed</p>
						<small>{formatDate(run.finishedAt ?? run.startedAt)}</small>
					</article>
				))}
			</div>
		</section>
	);
}
