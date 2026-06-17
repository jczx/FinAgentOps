import { ChatPlaceholder } from "./components/ChatPlaceholder";
import { CompanySelector } from "./components/CompanySelector";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { KpiCards } from "./components/KpiCards";
import { PipelineStatusPanel } from "./components/PipelineStatusPanel";
import { RiskScorePanel } from "./components/RiskScorePanel";
import { TrendChartPlaceholder } from "./components/TrendChartPlaceholder";
import { dashboardMock } from "./data/dashboardMock";

function App() {
	const { company, kpis, risk, pipeline, trend, analyst } = dashboardMock;

	return (
		<div className="app-shell">
			<Header />
			<main>
				<Hero company={company} />
				<section className="dashboard-grid" aria-label="Financial dashboard">
					<div className="dashboard-grid__primary">
						<CompanySelector company={company} />
						<KpiCards kpis={kpis} />
						<TrendChartPlaceholder data={trend} />
					</div>
					<aside className="dashboard-grid__sidebar" aria-label="Analysis panels">
						<RiskScorePanel risk={risk} />
						<PipelineStatusPanel pipeline={pipeline} />
						<ChatPlaceholder analyst={analyst} />
					</aside>
				</section>
			</main>
			<Footer />
		</div>
	);
}

export default App;
