import type { YearlyFinancialMetric } from "../data/dashboardTypes";

type FinancialChartsProps = {
	metrics: YearlyFinancialMetric[];
};

type SeriesConfig = {
	key: "revenue" | "netIncome" | "profitMargin" | "returnOnAssets" | "debtToAssetsRatio";
	label: string;
	unit: "currency" | "percent";
	className: string;
};

type ChartPoint = {
	x: number;
	y: number;
	label: string;
	value: number;
};

const financialSeries: SeriesConfig[] = [
	{
		key: "revenue",
		label: "Revenue",
		unit: "currency",
		className: "chart-line chart-line--primary",
	},
	{
		key: "netIncome",
		label: "Net income",
		unit: "currency",
		className: "chart-line chart-line--secondary",
	},
];

const ratioSeries: SeriesConfig[] = [
	{
		key: "profitMargin",
		label: "Profit margin",
		unit: "percent",
		className: "chart-line chart-line--primary",
	},
	{
		key: "returnOnAssets",
		label: "Return on assets",
		unit: "percent",
		className: "chart-line chart-line--secondary",
	},
	{
		key: "debtToAssetsRatio",
		label: "Debt-to-assets",
		unit: "percent",
		className: "chart-line chart-line--tertiary",
	},
];

function valueForSeries(
	metric: YearlyFinancialMetric,
	key: SeriesConfig["key"],
): number | null {
	return metric[key];
}

function formatChartValue(value: number, unit: SeriesConfig["unit"]): string {
	if (unit === "percent") {
		return `${value.toFixed(1)}%`;
	}

	return new Intl.NumberFormat("en-US", {
		compactDisplay: "short",
		currency: "USD",
		maximumFractionDigits: 1,
		notation: "compact",
		style: "currency",
	}).format(value);
}

function buildPoints(
	metrics: YearlyFinancialMetric[],
	series: SeriesConfig,
	minValue: number,
	maxValue: number,
): ChartPoint[] {
	const denominator = maxValue - minValue || 1;
	const width = 100;
	const height = 100;
	const horizontalStep = metrics.length > 1 ? width / (metrics.length - 1) : 0;

	return metrics.reduce<ChartPoint[]>((points, metric, index) => {
		const value = valueForSeries(metric, series.key);
		if (value === null || metric.fiscalYear === null) {
			return points;
		}

		points.push({
			x: index * horizontalStep,
			y: height - ((value - minValue) / denominator) * height,
			label: String(metric.fiscalYear),
			value,
		});
		return points;
	}, []);
}

function linePath(points: ChartPoint[]): string {
	return points.map((point) => `${point.x},${point.y}`).join(" ");
}

function ChartPanel({
	title,
	eyebrow,
	headingId,
	metrics,
	series,
}: {
	title: string;
	eyebrow: string;
	headingId: string;
	metrics: YearlyFinancialMetric[];
	series: SeriesConfig[];
}) {
	const values = series.flatMap((item) =>
		metrics
			.map((metric) => valueForSeries(metric, item.key))
			.filter((value): value is number => value !== null),
	);
	const minValue = values.length > 0 ? Math.min(...values) : 0;
	const maxValue = values.length > 0 ? Math.max(...values) : 1;
	const years = metrics
		.map((metric) => metric.fiscalYear)
		.filter((year): year is number => year !== null);

	return (
		<section className="panel chart-panel" aria-labelledby={headingId}>
			<div className="section-heading">
				<p className="eyebrow">{eyebrow}</p>
				<h2 id={headingId}>{title}</h2>
			</div>
			{metrics.length === 0 ? (
				<p className="empty-state">No yearly metrics are available yet.</p>
			) : (
				<>
					<div className="line-chart" role="img" aria-label={`${title} chart`}>
						<svg viewBox="0 0 100 100" preserveAspectRatio="none">
							<line x1="0" x2="100" y1="25" y2="25" className="chart-gridline" />
							<line x1="0" x2="100" y1="50" y2="50" className="chart-gridline" />
							<line x1="0" x2="100" y1="75" y2="75" className="chart-gridline" />
							{series.map((item) => {
								const points = buildPoints(metrics, item, minValue, maxValue);
								return (
									<polyline
										key={item.key}
										className={item.className}
										points={linePath(points)}
									/>
								);
							})}
						</svg>
					</div>
					<div className="chart-axis">
						<span>{years[0] ?? "N/A"}</span>
						<span>{years[years.length - 1] ?? "N/A"}</span>
					</div>
					<div className="chart-legend">
						{series.map((item) => {
							const latestMetric = [...metrics]
								.reverse()
								.find((metric) => valueForSeries(metric, item.key) !== null);
							const latestValue = latestMetric
								? valueForSeries(latestMetric, item.key)
								: null;

							return (
								<div className="chart-legend__item" key={item.key}>
									<span className={item.className} />
									<div>
										<strong>{item.label}</strong>
										<small>
											{latestValue === null
												? "Not available"
												: formatChartValue(latestValue, item.unit)}
										</small>
									</div>
								</div>
							);
						})}
					</div>
				</>
			)}
		</section>
	);
}

export function FinancialCharts({ metrics }: FinancialChartsProps) {
	return (
		<div className="chart-stack">
			<ChartPanel
				title="Revenue and net income"
				eyebrow="Yearly trend"
				headingId="financial-trend-heading"
				metrics={metrics}
				series={financialSeries}
			/>
			<ChartPanel
				title="Profitability and leverage"
				eyebrow="Ratio trend"
				headingId="ratio-trend-heading"
				metrics={metrics}
				series={ratioSeries}
			/>
		</div>
	);
}
