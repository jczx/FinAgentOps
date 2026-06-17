export function Header() {
	return (
		<header className="site-header">
			<a className="site-header__brand" href="/" aria-label="FinAgentOps home">
				<span className="site-header__mark" aria-hidden="true">
					F
				</span>
				<span>FinAgentOps</span>
			</a>
			<nav className="site-header__nav" aria-label="Dashboard navigation">
				<a href="#overview">Overview</a>
				<a href="#pipeline">Pipeline</a>
				<a href="#analyst">AI Analyst</a>
			</nav>
		</header>
	);
}
