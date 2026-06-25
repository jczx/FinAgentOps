import { useEffect, useState } from "react";
import { ChatPlaceholder } from "./components/ChatPlaceholder";
import { CompanyComparison } from "./components/CompanyComparison";
import { CompanySelector } from "./components/CompanySelector";
import { FinancialCharts } from "./components/FinancialCharts";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { KpiCards } from "./components/KpiCards";
import { PipelineStatusPanel } from "./components/PipelineStatusPanel";
import { analystPlaceholder } from "./data/dashboardPlaceholders";
import type { CompanyComparison as CompanyComparisonData } from "./data/dashboardTypes";
import {
	fetchComparisonData,
	fetchDashboardData,
	type DashboardApiData,
} from "./services/api";

const defaultComparisonTickers = ["AAPL", "MSFT", "NVDA"];

function App() {
	const [selectedTicker, setSelectedTicker] = useState("AAPL");
	const [selectedComparisonTickers, setSelectedComparisonTickers] = useState(
		defaultComparisonTickers,
	);
	const [dashboardData, setDashboardData] = useState<DashboardApiData | null>(
		null,
	);
	const [comparisonData, setComparisonData] = useState<CompanyComparisonData[]>(
		[],
	);
	const [errorMessage, setErrorMessage] = useState<string | null>(null);
	const [comparisonErrorMessage, setComparisonErrorMessage] = useState<
		string | null
	>(null);
	const [isLoading, setIsLoading] = useState(true);
	const [isComparisonLoading, setIsComparisonLoading] = useState(true);

	useEffect(() => {
		let isMounted = true;
		setIsLoading(true);

		fetchDashboardData(selectedTicker)
			.then((data) => {
				if (isMounted) {
					setDashboardData(data);
					setErrorMessage(null);
				}
			})
			.catch((error: Error) => {
				if (isMounted) {
					setErrorMessage(error.message);
				}
			})
			.finally(() => {
				if (isMounted) {
					setIsLoading(false);
				}
			});

		return () => {
			isMounted = false;
		};
	}, [selectedTicker]);

	useEffect(() => {
		let isMounted = true;

		if (selectedComparisonTickers.length === 0) {
			setComparisonData([]);
			setComparisonErrorMessage(null);
			setIsComparisonLoading(false);
			return () => {
				isMounted = false;
			};
		}

		setIsComparisonLoading(true);

		fetchComparisonData(selectedComparisonTickers)
			.then((data) => {
				if (isMounted) {
					setComparisonData(data);
					setComparisonErrorMessage(null);
				}
			})
			.catch((error: Error) => {
				if (isMounted) {
					setComparisonData([]);
					setComparisonErrorMessage(error.message);
				}
			})
			.finally(() => {
				if (isMounted) {
					setIsComparisonLoading(false);
				}
			});

		return () => {
			isMounted = false;
		};
	}, [selectedComparisonTickers]);

	const renderDashboard = () => {
		if (errorMessage) {
			return (
				<section className="state-panel" role="alert" aria-labelledby="error-title">
					<p className="eyebrow">Connection issue</p>
					<h1 id="error-title">Backend data is unavailable</h1>
					<p>{errorMessage}</p>
				</section>
			);
		}

		if (isLoading || dashboardData === null) {
			return (
				<section
					className="state-panel"
					aria-live="polite"
					aria-labelledby="loading-title"
				>
					<p className="eyebrow">Loading</p>
					<h1 id="loading-title">Loading financial data</h1>
					<p>Reading company records and yearly metrics from PostgreSQL.</p>
				</section>
			);
		}

		const { companies, company, kpis, yearlyMetrics, pipeline } = dashboardData;
		const latestMetric = yearlyMetrics[yearlyMetrics.length - 1];

		return (
			<>
				<Hero company={company} />
				<section className="dashboard-grid" aria-label="Financial dashboard">
					<div className="dashboard-grid__primary">
						<CompanySelector
							company={company}
							companies={companies}
							latestMetric={latestMetric}
							onTickerChange={setSelectedTicker}
						/>
						<KpiCards kpis={kpis} />
						<CompanyComparison
							companies={companies}
							comparisonData={comparisonData}
							errorMessage={comparisonErrorMessage}
							isLoading={isComparisonLoading}
							onSelectionChange={setSelectedComparisonTickers}
							selectedTickers={selectedComparisonTickers}
						/>
						<FinancialCharts metrics={yearlyMetrics} />
					</div>
					<aside className="dashboard-grid__sidebar" aria-label="Analysis panels">
						<PipelineStatusPanel pipeline={pipeline} />
						<ChatPlaceholder analyst={analystPlaceholder} />
					</aside>
				</section>
			</>
		);
	};

	return (
		<div className="app-shell">
			<Header />
			<main>{renderDashboard()}</main>
			<Footer />
		</div>
	);
}

export default App;
