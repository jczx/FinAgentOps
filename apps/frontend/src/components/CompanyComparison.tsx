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

type TrendPoint = {
	x: number;
	y: number;
};

const maxSelectedCompanies = 5;

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

function buildRevenueTrendPath(
	yearlyMetrics: YearlyFinancialMetric[],
	minValue: number,
	maxValue: number,
	years: number[],
): string {
	const denominator = maxValue - minValue || 1;
	const width = 100;
	const height = 100;
	const revenueByYear = new Map(
		yearlyMetrics
			.filter(
				(metric) => metric.fiscalYear !== null && metric.revenue !== null,
			)
			.map((metric) => [metric.fiscalYear as number, metric.revenue as number]),
	);

	const points = years.reduce<TrendPoint[]>((items, year, index) => {
		const value = revenueByYear.get(year);
		if (value === undefined) {
			return items;
		}

		items.push({
			x: years.length > 1 ? (index / (years.length - 1)) * width : width / 2,
			y: height - ((value - minValue) / denominator) * height,
		});
		return items;
	}, []);

	return points.map((point) => `${point.x},${point.y}`).join(" ");
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
	const allRevenueValues = comparisonData.flatMap((company) =>
		company.yearlyMetrics
			.map((metric) => metric.revenue)
			.filter((value): value is number => value !== null),
	);
	const minRevenue =
		allRevenueValues.length > 0 ? Math.min(...allRevenueValues) : 0;
	const maxRevenue =
		allRevenueValues.length > 0 ? Math.max(...allRevenueValues) : 1;
	const trendYears = [
		...new Set(
			comparisonData.flatMap((company) =>
				company.yearlyMetrics
					.map((metric) => metric.fiscalYear)
					.filter((year): year is number => year !== null),
			),
		),
	].sort((left, right) => left - right);

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

					<div
						className="comparison-trend"
						role="img"
						aria-label="Revenue trend comparison"
					>
						<svg viewBox="0 0 100 100" preserveAspectRatio="none">
							<line x1="0" x2="100" y1="25" y2="25" className="chart-gridline" />
							<line x1="0" x2="100" y1="50" y2="50" className="chart-gridline" />
							<line x1="0" x2="100" y1="75" y2="75" className="chart-gridline" />
							{comparisonData.map((company, index) => (
								<polyline
									className={`comparison-trend__line comparison-trend__line--${index + 1}`}
									key={company.ticker}
									points={buildRevenueTrendPath(
										company.yearlyMetrics,
										minRevenue,
										maxRevenue,
										trendYears,
									)}
								/>
							))}
						</svg>
					</div>
					<div className="chart-axis">
						<span>{trendYears[0] ?? "N/A"}</span>
						<span>{trendYears[trendYears.length - 1] ?? "N/A"}</span>
					</div>
					<div className="comparison-legend">
						{comparisonData.map((company, index) => (
							<span key={company.ticker}>
								<i className={`comparison-trend__line--${index + 1}`} />
								{company.ticker}
							</span>
						))}
					</div>
				</>
			)}
		</section>
	);
}
