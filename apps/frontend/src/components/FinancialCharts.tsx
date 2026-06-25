import { useEffect, useMemo, useRef } from "react";
import {
	ColorType,
	CrosshairMode,
	createChart,
	LineSeries,
	LineStyle,
	type IChartApi,
	type LineData,
	type Time,
} from "lightweight-charts";
import type { YearlyFinancialMetric } from "../data/dashboardTypes";

type FinancialChartsProps = {
	metrics: YearlyFinancialMetric[];
};

type SeriesKey =
	| "revenue"
	| "netIncome"
	| "profitMargin"
	| "returnOnAssets"
	| "debtToAssetsRatio";

type TradingSeriesConfig = {
	key: SeriesKey;
	label: string;
	unit: "currency" | "percent";
	color: string;
	lineStyle?: LineStyle;
};

type TradingChartProps = {
	eyebrow: string;
	headingId: string;
	metrics: YearlyFinancialMetric[];
	series: TradingSeriesConfig[];
	title: string;
};

const financialSeries: TradingSeriesConfig[] = [
	{
		key: "revenue",
		label: "Revenue",
		unit: "currency",
		color: "#f5f5f5",
	},
	{
		key: "netIncome",
		label: "Net income",
		unit: "currency",
		color: "#b3b3b3",
	},
];

const ratioSeries: TradingSeriesConfig[] = [
	{
		key: "profitMargin",
		label: "Profit margin",
		unit: "percent",
		color: "#f5f5f5",
	},
	{
		key: "returnOnAssets",
		label: "Return on assets",
		unit: "percent",
		color: "#b3b3b3",
	},
	{
		key: "debtToAssetsRatio",
		label: "Debt-to-assets",
		unit: "percent",
		color: "#7a7a7a",
		lineStyle: LineStyle.Dashed,
	},
];

function valueForSeries(
	metric: YearlyFinancialMetric,
	key: SeriesKey,
): number | null {
	return metric[key];
}

function metricTime(metric: YearlyFinancialMetric): Time | null {
	if (metric.fiscalYear === null) {
		return null;
	}

	return `${metric.fiscalYear}-12-31`;
}

function formatChartValue(
	value: number | null,
	unit: TradingSeriesConfig["unit"],
): string {
	if (value === null) {
		return "Not available";
	}

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

function seriesData(
	metrics: YearlyFinancialMetric[],
	series: TradingSeriesConfig,
): LineData<Time>[] {
	return metrics.reduce<LineData<Time>[]>((items, metric) => {
		const time = metricTime(metric);
		const value = valueForSeries(metric, series.key);

		if (time === null || value === null) {
			return items;
		}

		items.push({ time, value });
		return items;
	}, []);
}

function latestValue(
	metrics: YearlyFinancialMetric[],
	key: SeriesKey,
): number | null {
	for (let index = metrics.length - 1; index >= 0; index -= 1) {
		const value = valueForSeries(metrics[index], key);
		if (value !== null) {
			return value;
		}
	}

	return null;
}

function TradingChart({
	eyebrow,
	headingId,
	metrics,
	series,
	title,
}: TradingChartProps) {
	const containerRef = useRef<HTMLDivElement | null>(null);
	const chartRef = useRef<IChartApi | null>(null);
	const dataBySeries = useMemo(
		() =>
			series.map((item) => ({
				...item,
				data: seriesData(metrics, item),
				latestValue: latestValue(metrics, item.key),
			})),
		[metrics, series],
	);
	const hasData = dataBySeries.some((item) => item.data.length > 0);

	useEffect(() => {
		const container = containerRef.current;
		if (!container || !hasData) {
			return undefined;
		}

		const chart = createChart(container, {
			autoSize: true,
			crosshair: {
				mode: CrosshairMode.Normal,
				horzLine: {
					color: "rgba(245, 245, 245, 0.22)",
					labelBackgroundColor: "#111111",
				},
				vertLine: {
					color: "rgba(245, 245, 245, 0.22)",
					labelBackgroundColor: "#111111",
					style: LineStyle.Dashed,
				},
			},
			grid: {
				horzLines: { color: "rgba(255, 255, 255, 0.06)" },
				vertLines: { color: "rgba(255, 255, 255, 0.04)" },
			},
			layout: {
				background: { color: "#111111", type: ColorType.Solid },
				fontFamily:
					"Inter, Manrope, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
				textColor: "#b3b3b3",
			},
			localization: {
				priceFormatter: (value: number) =>
					series[0]?.unit === "percent"
						? `${value.toFixed(1)}%`
						: new Intl.NumberFormat("en-US", {
								compactDisplay: "short",
								maximumFractionDigits: 1,
								notation: "compact",
							}).format(value),
			},
			rightPriceScale: {
				borderColor: "rgba(255, 255, 255, 0.12)",
				scaleMargins: {
					bottom: 0.18,
					top: 0.12,
				},
			},
			timeScale: {
				borderColor: "rgba(255, 255, 255, 0.12)",
				fixLeftEdge: true,
				fixRightEdge: true,
				timeVisible: true,
			},
		});
		chartRef.current = chart;

		for (const item of dataBySeries) {
			if (item.data.length === 0) {
				continue;
			}

			const line = chart.addSeries(LineSeries, {
				color: item.color,
				crosshairMarkerBorderColor: "#0a0a0a",
				crosshairMarkerBorderWidth: 2,
				crosshairMarkerRadius: 4,
				crosshairMarkerVisible: true,
				lastValueVisible: true,
				lineStyle: item.lineStyle ?? LineStyle.Solid,
				lineWidth: 2,
				priceLineColor: "rgba(245, 245, 245, 0.18)",
				priceLineStyle: LineStyle.Dotted,
				priceLineVisible: true,
				priceFormat:
					item.unit === "percent"
						? { type: "custom", formatter: (value: number) => `${value.toFixed(1)}%` }
						: { type: "volume" },
				title: item.label,
			});
			line.setData(item.data);
		}

		chart.timeScale().fitContent();

		return () => {
			chart.remove();
			chartRef.current = null;
		};
	}, [dataBySeries, hasData, series]);

	return (
		<section className="panel chart-panel trading-chart-panel" aria-labelledby={headingId}>
			<div className="section-heading trading-chart-panel__heading">
				<div>
					<p className="eyebrow">{eyebrow}</p>
					<h2 id={headingId}>{title}</h2>
				</div>
				<span>Yearly SEC facts</span>
			</div>
			{hasData ? (
				<>
					<div
						ref={containerRef}
						className="trading-chart"
						role="img"
						aria-label={`${title} chart`}
					/>
					<div className="trading-chart-legend">
						{dataBySeries.map((item) => (
							<div className="trading-chart-legend__item" key={item.key}>
								<span style={{ backgroundColor: item.color }} />
								<div>
									<strong>{item.label}</strong>
									<small>{formatChartValue(item.latestValue, item.unit)}</small>
								</div>
							</div>
						))}
					</div>
				</>
			) : (
				<p className="empty-state">No yearly metrics are available yet.</p>
			)}
		</section>
	);
}

export function FinancialCharts({ metrics }: FinancialChartsProps) {
	return (
		<div className="chart-stack">
			<TradingChart
				title="Revenue and net income"
				eyebrow="TradingView-style trend"
				headingId="financial-trend-heading"
				metrics={metrics}
				series={financialSeries}
			/>
			<TradingChart
				title="Profitability and leverage"
				eyebrow="Ratio analytics"
				headingId="ratio-trend-heading"
				metrics={metrics}
				series={ratioSeries}
			/>
		</div>
	);
}
