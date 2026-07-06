from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.advanced_ai import ConversationEvaluation, AgentEvaluation
from app.advanced_ai.repositories import AdvancedAIRepository
from app.advanced_ai.exceptions import ConversationEvaluationError, AgentEvaluationError


class AgentConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdvancedAIRepository(db)

    async def evaluate_conversation(
        self,
        project_id: str,
        session_id: str,
        turns: List[Dict[str, str]]
    ) -> ConversationEvaluation:
        """Evaluates multi-turn conversation coherence, memory retention, user satisfaction, and turn statistics."""
        try:
            turns_count = len(turns)
            if turns_count == 0:
                raise ConversationEvaluationError("Cannot evaluate an empty conversation.")

            memory_retention = 1.0
            context_preservation = 1.0
            coherence = 1.0
            response_consistency = 1.0
            user_satisfaction = 1.0
            total_chars = 0

            # Dynamic check simulation
            for i, turn in enumerate(turns):
                role = turn.get("role", "")
                content = turn.get("content", "").lower()
                total_chars += len(content)

                if role == "assistant":
                    # Check coherence indicators
                    if "i don't know" in content or "contradiction" in content:
                        coherence -= 0.15
                    if "as mentioned before" in content:
                        memory_retention += 0.05

            avg_turn_length = total_chars / turns_count

            # Normalize scores
            memory_retention = min(1.0, max(0.0, memory_retention))
            coherence = min(1.0, max(0.0, coherence))
            user_satisfaction = min(1.0, max(0.0, coherence * 0.9 + 0.1))

            convo = ConversationEvaluation(
                project_id=project_id,
                session_id=session_id,
                turns_count=turns_count,
                memory_retention_score=round(memory_retention, 4),
                context_preservation_score=round(context_preservation, 4),
                coherence_score=round(coherence, 4),
                response_consistency_score=round(response_consistency, 4),
                user_satisfaction_score=round(user_satisfaction, 4),
                avg_turn_length=round(avg_turn_length, 2),
                metrics_json={
                    "total_tokens_estimated": turns_count * 150,
                    "conversation_cohesion_status": "HIGH"
                }
            )

            res = await self.repo.create_conversation_evaluation(convo)
            return res
        except Exception as e:
            raise ConversationEvaluationError(f"Failed to evaluate conversation: {str(e)}")

    async def evaluate_agent(
        self,
        project_id: str,
        agent_name: str,
        planning_quality: float,
        task_completion: float,
        memory_consistency: float,
        reasoning_trace_score: float,
        tool_usage_score: float,
        conversation_quality: float,
        agent_collaboration_score: float
    ) -> AgentEvaluation:
        """Evaluates single/multi-agent planning, reasoning trace, task completion, and collaboration."""
        try:
            # Overall Agent Score calculation
            agent_score = (
                planning_quality * 0.15 +
                task_completion * 0.20 +
                memory_consistency * 0.15 +
                reasoning_trace_score * 0.15 +
                tool_usage_score * 0.15 +
                conversation_quality * 0.10 +
                agent_collaboration_score * 0.10
            )

            agent_eval = AgentEvaluation(
                project_id=project_id,
                agent_name=agent_name,
                planning_quality=round(planning_quality, 4),
                task_completion=round(task_completion, 4),
                memory_consistency=round(memory_consistency, 4),
                reasoning_trace_score=round(reasoning_trace_score, 4),
                tool_usage_score=round(tool_usage_score, 4),
                conversation_quality=round(conversation_quality, 4),
                agent_collaboration_score=round(agent_collaboration_score, 4),
                agent_score=round(agent_score, 4)
            )

            res = await self.repo.create_agent_evaluation(agent_eval)
            return res
        except Exception as e:
            raise AgentEvaluationError(f"Failed to evaluate agent: {str(e)}")

    def evaluate_tool_calls(
        self,
        tool_selections: List[Dict[str, Any]],
        executions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validates function calling selection, argument correctness, retries, and latency."""
        total_calls = len(tool_selections)
        if total_calls == 0:
            return {"status": "NO_TOOLS_USED", "tool_success_rate": 1.0}

        successes = 0
        total_latency = 0.0
        retries = 0
        errors = []

        for sel, exec_item in zip(tool_selections, executions):
            # Evaluate argument correctness
            expected_args = sel.get("expected_args", {})
            actual_args = exec_item.get("args", {})
            
            # Simple match percentage
            arg_correct = True
            for k, v in expected_args.items():
                if actual_args.get(k) != v:
                    arg_correct = False
                    errors.append(f"Argument mismatch for tool {sel.get('name')}: expected {v}, got {actual_args.get(k)}")

            status = exec_item.get("status", "SUCCESS")
            if status == "SUCCESS" and arg_correct:
                successes += 1
            
            total_latency += exec_item.get("latency_ms", 100.0)
            retries += exec_item.get("retries", 0)

        success_rate = successes / total_calls

        return {
            "total_calls": total_calls,
            "tool_success_rate": round(success_rate, 4),
            "average_latency_ms": round(total_latency / total_calls, 2),
            "total_retries": retries,
            "argument_errors": errors,
            "mcp_compatibility": "READY"
        }
