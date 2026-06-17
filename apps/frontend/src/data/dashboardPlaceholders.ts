import type { AnalystMessage, TrendPoint } from "./dashboardTypes";

export const trendPlaceholder: TrendPoint[] = [
	{ label: "Q1", value: 62 },
	{ label: "Q2", value: 68 },
	{ label: "Q3", value: 72 },
	{ label: "Q4", value: 77 },
];

export const analystPlaceholder: AnalystMessage[] = [
	{
		role: "assistant",
		text: "The AI analyst will summarize financial signals after RAG is added.",
	},
	{
		role: "user",
		text: "What changed in revenue growth this quarter?",
	},
];
