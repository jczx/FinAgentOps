import type { Company } from "../data/dashboardTypes";

type CompanySelectorProps = {
	company: Company;
};

export function CompanySelector({ company }: CompanySelectorProps) {
	return (
		<section className="panel company-selector" aria-labelledby="company-heading">
			<div>
				<p className="eyebrow">Selected company</p>
				<h2 id="company-heading">{company.name}</h2>
				<p>
					{company.ticker} · {company.exchange} · {company.sector}
				</p>
			</div>
			<button className="button" type="button">
				Change company
			</button>
		</section>
	);
}
