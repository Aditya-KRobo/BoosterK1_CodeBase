from booster_robotics_sdk_python import (
    B1LocoClient,
    RobotMode,
    AiClient,
    StartAiChatParameter,
    AsrConfig,
    LlmConfig,
    TtsConfig,
    GetModeResponse,
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


def autonomous_life_start(loco: B1LocoClient, ai: AiClient):
    print("Entering Autonomous Life Mode...")

    gm: GetModeResponse = GetModeResponse()
    res = loco.GetMode(gm)
    if res == 0:
        print(f"[INFO] Mode: {gm.mode}")

    if gm.mode != RobotMode.kCustom:
        print(
            "[WARN] Robot not in Custom mode, possible issue. Skipping Autonomous Life start command."
        )
        return -1

    res = loco.GetUp()
    if res != 0:
        print("[ERROR] Failed to execute GetUp command.")
        return -1

    param = build_default_start_param(enable_face_tracking=False)
    res = ai.StartAiChat(param)
    if res != 0:
        print("[ERROR] Failed to start AI Chat.")
        return -1

    res = ai.StartFaceTracking()
    if res != 0:
        print("[ERROR] Failed to start face tracking.")
        return -1


def autonomous_life_stop(loco: B1LocoClient, ai: AiClient):
    print("Entering Autonomous Life Mode...")

    gm: GetModeResponse = GetModeResponse()
    res = loco.GetMode(gm)
    if res == 0:
        print(f"[INFO] Mode: {gm.mode}")

    if gm.mode != RobotMode.kCustom:
        print(
            "[WARN] Robot not in Custom mode, possible issue. Skipping Autonomous Life stop command."
        )
        return -1

    res = ai.StopAiChat()
    if res != 0:
        print("[ERROR] Failed to stop AI Chat.")
        return -1

    res = ai.StopFaceTracking()
    if res != 0:
        print("[ERROR] Failed to stop face tracking.")
        return -1
