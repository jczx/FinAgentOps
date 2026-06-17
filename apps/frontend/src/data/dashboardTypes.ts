export type Company = {
	name: string;
	ticker: string;
	exchange: string;
	sector: string;
};

export type Kpi = {
	label: string;
	value: string;
	description: string;
	trend: "up" | "down" | "flat";
};

export type RiskProfile = {
	score: "Low" | "Medium" | "High";
	summary: string;
	factors: string[];
};

export type PipelineStatus = {
	status: "Success" | "Warning" | "Failed";
	lastRun: string;
	stepsCompleted: number;
	totalSteps: number;
};

export type TrendPoint = {
	label: string;
	value: number;
};

export type AnalystMessage = {
	role: "assistant" | "user";
	text: string;
};
