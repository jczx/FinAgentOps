import type { Company, YearlyFinancialMetric } from "../data/dashboardTypes";

type CompanySelectorProps = {
	company: Company;
	companies: Company[];
	latestMetric: YearlyFinancialMetric | undefined;
	onTickerChange: (ticker: string) => void;
};

function formatDateTime(value: string | null | undefined): string {
	if (!value) {
		return "Not available";
	}

	return new Intl.DateTimeFormat("en-US", {
		dateStyle: "medium",
		timeStyle: "short",
	}).format(new Date(value));
}

export function CompanySelector({
	company,
	companies,
	latestMetric,
	onTickerChange,
}: CompanySelectorProps) {
	const latestYear = latestMetric?.fiscalYear ?? "N/A";
	const updatedAt = formatDateTime(latestMetric?.updatedAt);

	return (
		<section className="panel company-selector" aria-labelledby="company-heading">
			<div className="company-selector__summary">
				<p className="eyebrow">Selected company</p>
				<h2 id="company-heading">{company.name}</h2>
				<p>
					{company.ticker} / {company.exchange} / {company.sector}
				</p>
				<div className="company-selector__meta" aria-label="Metric freshness">
					<span>Latest fiscal year: {latestYear}</span>
					<span>Metrics updated: {updatedAt}</span>
				</div>
			</div>
			<label className="company-selector__control">
				<span>Company</span>
				<select
					value={company.ticker}
					onChange={(event) => onTickerChange(event.target.value)}
				>
					{companies.map((option) => (
						<option key={option.ticker} value={option.ticker}>
							{option.ticker} - {option.name}
						</option>
					))}
				</select>
			</label>
		</section>
	);
}
