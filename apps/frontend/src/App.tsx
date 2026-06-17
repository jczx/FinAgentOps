import { useEffect, useState } from "react";
import { ChatPlaceholder } from "./components/ChatPlaceholder";
import { CompanySelector } from "./components/CompanySelector";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { KpiCards } from "./components/KpiCards";
import { PipelineStatusPanel } from "./components/PipelineStatusPanel";
import { RiskScorePanel } from "./components/RiskScorePanel";
import { TrendChartPlaceholder } from "./components/TrendChartPlaceholder";
import {
	analystPlaceholder,
	trendPlaceholder,
} from "./data/dashboardPlaceholders";
import { fetchDashboardData, type DashboardApiData } from "./services/api";

function App() {
	const [dashboardData, setDashboardData] = useState<DashboardApiData | null>(
		null,
	);
	const [errorMessage, setErrorMessage] = useState<string | null>(null);

	useEffect(() => {
		let isMounted = true;

		fetchDashboardData("AAPL")
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
			});

		return () => {
			isMounted = false;
		};
	}, []);

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

		if (dashboardData === null) {
			return (
				<section
					className="state-panel"
					aria-live="polite"
					aria-labelledby="loading-title"
				>
					<p className="eyebrow">Loading</p>
					<h1 id="loading-title">Loading dashboard data</h1>
					<p>Fetching mock financial data from the FastAPI backend.</p>
				</section>
			);
		}

		const { company, kpis, risk, pipeline } = dashboardData;

		return (
			<>
				<Hero company={company} />
				<section className="dashboard-grid" aria-label="Financial dashboard">
					<div className="dashboard-grid__primary">
						<CompanySelector company={company} />
						<KpiCards kpis={kpis} />
						<TrendChartPlaceholder data={trendPlaceholder} />
					</div>
					<aside className="dashboard-grid__sidebar" aria-label="Analysis panels">
						<RiskScorePanel risk={risk} />
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
