import sys

from agents.components import LLM
from agents.clients import OllamaClient
from agents.models import OllamaModel
from agents.config import LLMConfig
from agents.ros import Topic, Launcher
from ros_sugar.io.supported_types import String

from security_agents.secure_agent import SecureAgent
from security.policy_engine import PolicyEngine


MODEL_NAME = "llama3.2:3b"
HOST = "localhost"


def get_coordinates(position: list[float]) -> str:
    """Process a three-dimensional position."""

    print("\n[TOOL EXECUTED] get_coordinates")
    print("[TOOL ARGUMENTS]", position)

    return (
        f"Coordinates processed: "
        f"x={position[0]}, y={position[1]}, z={position[2]}"
    )


def main():

    if len(sys.argv) != 2 or sys.argv[1] not in ("baseline", "secure"):
        print("Uso: python3 minimal_llm_experiment.py [baseline|secure]")
        sys.exit(1)

    mode = sys.argv[1]

    print(f"\n========== EXPERIMENTO: {mode.upper()} ==========\n")

    # --------------------------------------------------------
    # MODELO
    # --------------------------------------------------------

    model = OllamaModel(
        name="llama",
        checkpoint=MODEL_NAME
    )

    client = OllamaClient(
        model=model,
        host=HOST
    )

    if not client.supports_tool_calls:
        raise RuntimeError("El modelo no admite llamadas a herramientas.")

    # --------------------------------------------------------
    # TOPICS
    # --------------------------------------------------------

    input_topic = Topic(
        name="goto_in",
        msg_type=String
    )

    output_topic = Topic(
        name="security_test_output",
        msg_type=String
    )

    # --------------------------------------------------------
    # LLM
    # --------------------------------------------------------

    config = LLMConfig(
        enable_rag=False,
        temperature=0.1,
        max_new_tokens=128,
        _system_prompt=(
            "You are a robotics assistant. "
            "You must use the get_coordinates tool to process "
            "the requested position. Do not answer without "
            "calling this tool."
        )
    )

    llm = LLM(
        inputs=[input_topic],
        outputs=[output_topic],
        model_client=client,
        config=config,
        trigger=input_topic,
        component_name="security_test_llm"
    )

    llm.set_component_prompt(
        template=(
            "Process the following request: {{ goto_in }}\n"
            "You must call get_coordinates with the requested "
            "position. Do not invent or modify coordinates."
        )
    )

    # --------------------------------------------------------
    # DESCRIPCIÓN DE LA HERRAMIENTA
    # --------------------------------------------------------

    function_description = {
        "type": "function",
        "function": {
            "name": "get_coordinates",
            "description": "Process a position in 3D space.",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                        "description": "Position coordinates [x, y, z]."
                    }
                },
                "required": ["position"],
                "additionalProperties": False
            }
        }
    }

    # --------------------------------------------------------
    # REGISTRO
    # --------------------------------------------------------

    secure_agent = None

    if mode == "baseline":

        print("[BASELINE] Registering tool without security.")

        llm.register_tool(
            tool=get_coordinates,
            tool_description=function_description,
            send_tool_response_to_model=False
        )

    else:

        print("[SECURE] Registering tool through SecureAgent.")

        secure_agent = SecureAgent(
            policy_engine=PolicyEngine()
        )

        secure_agent.register_tool(
            component=llm,
            tool=get_coordinates,
            tool_description=function_description,
            send_tool_response_to_model=False
        )

    # --------------------------------------------------------
    # LANZAMIENTO
    # --------------------------------------------------------

    launcher = Launcher()

    launcher.add_pkg(
        components=[llm],
        package_name="automatika_embodied_agents",
        multiprocessing=False
    )

    try:
        print("\n[INFO] Starting ROS 2 component...")
        print("[INFO] Input topic: /goto_in")
        print("[INFO] Output topic: /security_test_output")

        launcher.bringup()

    except KeyboardInterrupt:
        print("\n[INFO] Experiment interrupted.")

    finally:

        if secure_agent is not None:

            print("\n========== SECURITY AUDIT ==========")

            for event in secure_agent.get_audit_log():
                print(event)

        print("\n[INFO] Experiment finished.")


if __name__ == "__main__":
    main()