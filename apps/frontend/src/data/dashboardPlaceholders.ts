import type { AnalystMessage } from "./dashboardTypes";

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
