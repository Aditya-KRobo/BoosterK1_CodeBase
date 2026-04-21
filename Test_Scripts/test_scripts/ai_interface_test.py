from booster_robotics_sdk_python import (
    B1LocoClient,
    AiClient,
    ChannelFactory,
    StartAiChatParameter,
    TtsConfig,
    LlmConfig,
    AsrConfig,
    SpeakParameter,
    RobotMode,
    Position,
    Orientation,
    Posture,
    GetModeResponse,
    Quaternion,
    Frame,
    Transform,
)
import sys, time, random


def build_default_start_param(
    enable_face_tracking: bool = False,
) -> StartAiChatParameter:
    """
    Build a sample StartAiChatParameter.
    Adjust system_prompt / welcome_msg / TTS / ASR as needed.
    """
    # Example TTS configuration
    tts = TtsConfig(
        voice_type="zh_male_wennuanahu_moon_bigtts",
        ignore_bracket_text=[1, 2],
    )

    # Example LLM configuration
    llm = LlmConfig(
        system_prompt="You are a helpful humanoid robot assistant.",
        welcome_msg="Hello, I am the Booster robot assistant.",
        prompt_name="default",
    )

    # Example ASR configuration
    asr = AsrConfig(
        interrupt_speech_duration=800,
        interrupt_keywords=["stop", "hold on", "do not speak"],
    )

    p = StartAiChatParameter()
    p.interrupt_mode = True
    p.tts_config = tts
    p.llm_config = llm
    p.asr_config = asr
    p.enable_face_tracking = enable_face_tracking
    return p


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    net_if = sys.argv[1]
    robot_name = sys.argv[2] if len(sys.argv) > 2 else None

    ChannelFactory.Instance().Init(0, net_if)

    client = AiClient()
    client.Init()

    print("AI CLI started.")
    res = 0

    while True:
        try:
            input_cmd = input(
            "Here is the command list:\
                          \n1. Start face tracking -> ft\
                          \n2. Stop face tracking -> sft\
                          \n3. Stop Ai Chat -> stp\
                          \n....."
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExit.")
            break

        if not input_cmd:
            continue
        
        parts = input_cmd.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        param = build_default_start_param(enable_face_tracking=True)
        client.StartAiChat(param)
        print("[OK] StartAiChat (face_tracking = True) sent.")

        if cmd == "ft":
            param = build_default_start_param(enable_face_tracking=True)
            res = client.StartAiChat(param)
            print("[OK] StartAiChat (face_tracking = True) sent.")
        elif cmd == "sft":
            param = build_default_start_param(enable_face_tracking=False)
            res = client.StartAiChat(param)
            print("[OK] StartAiChat (face_tracking = False) sent.")
        elif cmd == "stp":
            res = client.StopAiChat()
            print("[OK] StopAiChat sent.")
        elif cmd == "speak":
                if not arg:
                    print("Usage: speak <text>")
                    continue
                sp = SpeakParameter(arg)
                client.Speak(sp)
                print(f"[OK] Speak sent: {arg}")

        if res != 0:
            print(f"Request failed: error = {res}")


if __name__ == "__main__":
    main()
