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
import type {
	Company,
	CompanyComparison,
	YearlyFinancialMetric,
} from "../data/dashboardTypes";

type CompanyComparisonProps = {
	companies: Company[];
	comparisonData: CompanyComparison[];
	errorMessage: string | null;
	isLoading: boolean;
	onSelectionChange: (tickers: string[]) => void;
	selectedTickers: string[];
};

type CompareMetricKey =
	| "revenue"
	| "netIncome"
	| "profitMargin"
	| "returnOnAssets"
	| "debtToAssetsRatio";

type CompareMetric = {
	key: CompareMetricKey;
	label: string;
	unit: "currency" | "percent";
	lowerIsBetter?: boolean;
};

const maxSelectedCompanies = 5;
const comparisonColors = ["#f5f5f5", "#cfcfcf", "#a8a8a8", "#7a7a7a", "#5f5f5f"];

const compareMetrics: CompareMetric[] = [
	{ key: "revenue", label: "Revenue", unit: "currency" },
	{ key: "netIncome", label: "Net income", unit: "currency" },
	{ key: "profitMargin", label: "Profit margin", unit: "percent" },
	{ key: "returnOnAssets", label: "Return on assets", unit: "percent" },
	{
		key: "debtToAssetsRatio",
		label: "Debt-to-assets",
		unit: "percent",
		lowerIsBetter: true,
	},
];

function valueForMetric(
	metric: YearlyFinancialMetric | null,
	key: CompareMetricKey,
): number | null {
	if (!metric) {
		return null;
	}

	return metric[key];
}

function formatValue(value: number | null, unit: CompareMetric["unit"]): string {
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

function metricTime(metric: YearlyFinancialMetric): Time | null {
	if (metric.fiscalYear === null) {
		return null;
	}

	return `${metric.fiscalYear}-12-31`;
}

function revenueSeriesData(metrics: YearlyFinancialMetric[]): LineData<Time>[] {
	return metrics.reduce<LineData<Time>[]>((items, metric) => {
		const time = metricTime(metric);
		if (time === null || metric.revenue === null) {
			return items;
		}

		items.push({ time, value: metric.revenue });
		return items;
	}, []);
}

function latestRevenue(metrics: YearlyFinancialMetric[]): number | null {
	for (let index = metrics.length - 1; index >= 0; index -= 1) {
		const revenue = metrics[index].revenue;
		if (revenue !== null) {
			return revenue;
		}
	}

	return null;
}

function ComparisonRevenueChart({
	comparisonData,
}: {
	comparisonData: CompanyComparison[];
}) {
	const containerRef = useRef<HTMLDivElement | null>(null);
	const chartRef = useRef<IChartApi | null>(null);
	const series = useMemo(
		() =>
			comparisonData.map((company, index) => ({
				color: comparisonColors[index] ?? "#5f5f5f",
				data: revenueSeriesData(company.yearlyMetrics),
				latestRevenue: latestRevenue(company.yearlyMetrics),
				ticker: company.ticker,
			})),
		[comparisonData],
	);
	const hasData = series.some((item) => item.data.length > 0);

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
					new Intl.NumberFormat("en-US", {
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

		for (const item of series) {
			if (item.data.length === 0) {
				continue;
			}

			const line = chart.addSeries(LineSeries, {
				color: item.color,
				crosshairMarkerBorderColor: "#0a0a0a",
				crosshairMarkerBorderWidth: 2,
				crosshairMarkerRadius: 4,
				lastValueVisible: true,
				lineWidth: 2,
				priceFormat: { type: "volume" },
				priceLineColor: "rgba(245, 245, 245, 0.16)",
				priceLineStyle: LineStyle.Dotted,
				title: item.ticker,
			});
			line.setData(item.data);
		}

		chart.timeScale().fitContent();

		return () => {
			chart.remove();
			chartRef.current = null;
		};
	}, [hasData, series]);

	if (!hasData) {
		return <p className="empty-state">No revenue trend data is available yet.</p>;
	}

	return (
		<>
			<div
				ref={containerRef}
				className="comparison-trading-chart"
				role="img"
				aria-label="Revenue trend comparison"
			/>
			<div className="comparison-legend">
				{series.map((company) => (
					<span key={company.ticker}>
						<i style={{ color: company.color }} />
						{company.ticker}
						<small>{formatValue(company.latestRevenue, "currency")}</small>
					</span>
				))}
			</div>
		</>
	);
}

export function CompanyComparison({
	companies,
	comparisonData,
	errorMessage,
	isLoading,
	onSelectionChange,
	selectedTickers,
}: CompanyComparisonProps) {
	const selectedSet = new Set(selectedTickers);
	const hasReachedLimit = selectedTickers.length >= maxSelectedCompanies;

	const toggleTicker = (ticker: string) => {
		if (selectedSet.has(ticker)) {
			onSelectionChange(
				selectedTickers.filter((selectedTicker) => selectedTicker !== ticker),
			);
			return;
		}

		if (hasReachedLimit) {
			return;
		}

		onSelectionChange([...selectedTickers, ticker]);
	};

	return (
		<section className="panel comparison-panel" aria-labelledby="comparison-heading">
			<div className="section-heading comparison-panel__heading">
				<div>
					<p className="eyebrow">Peer comparison</p>
					<h2 id="comparison-heading">Compare companies</h2>
				</div>
				<span>{selectedTickers.length}/{maxSelectedCompanies} selected</span>
			</div>

			<div className="comparison-selector" aria-label="Company comparison selector">
				{companies.map((company) => {
					const checked = selectedSet.has(company.ticker);
					const disabled = !checked && hasReachedLimit;

					return (
						<label className="comparison-toggle" key={company.ticker}>
							<input
								checked={checked}
								disabled={disabled}
								onChange={() => toggleTicker(company.ticker)}
								type="checkbox"
							/>
							<span>{company.ticker}</span>
						</label>
					);
				})}
			</div>

			{errorMessage && (
				<p className="comparison-panel__message" role="alert">
					{errorMessage}
				</p>
			)}

			{isLoading ? (
				<p className="empty-state">Loading peer metrics from PostgreSQL.</p>
			) : comparisonData.length === 0 ? (
				<p className="empty-state">
					Select at least one company to compare yearly financial metrics.
				</p>
			) : (
				<>
					<div className="comparison-table" aria-label="Latest fiscal year comparison">
						<div className="comparison-table__header">
							<span>Company</span>
							{compareMetrics.map((metric) => (
								<span key={metric.key}>{metric.label}</span>
							))}
						</div>
						{comparisonData.map((company) => (
							<div className="comparison-table__row" key={company.ticker}>
								<strong>
									{company.ticker}
									<small>{company.latestMetric?.fiscalYear ?? "N/A"}</small>
								</strong>
								{compareMetrics.map((metric) => {
									const value = valueForMetric(company.latestMetric, metric.key);
									return (
										<span key={metric.key}>
											{formatValue(value, metric.unit)}
										</span>
									);
								})}
							</div>
						))}
					</div>

					<div className="comparison-chart-block">
						<div className="comparison-chart-block__heading">
							<strong>Revenue trend</strong>
							<span>TradingView-style peer view</span>
						</div>
						<ComparisonRevenueChart comparisonData={comparisonData} />
					</div>
				</>
			)}
		</section>
	);
}
