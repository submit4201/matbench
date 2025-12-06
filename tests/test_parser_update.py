from src.engine.xml_parser import parse_llm_response
from src.agents.base_agent import ActionType

def test_parser():
    xml = """
    <THINKING>I should ally with p2.</THINKING>
    <NEXT_ACTION>
        <ALLIANCE>
            <TARGET>p2</TARGET>
            <DURATION>5</DURATION>
        </ALLIANCE>
        <BUYOUT>
            <TARGET>p3</TARGET>
            <OFFER>5000</OFFER>
        </BUYOUT>
    </NEXT_ACTION>
    """
    
    parsed = parse_llm_response(xml)
    
    print(f"Raw: {parsed.raw_response}")
    print(f"Thinking: {parsed.thinking}")
    print(f"Errors: {parsed.parse_errors}")
    print(f"Actions: {len(parsed.actions)}")
    
    for a in parsed.actions:
        print(f"Action: {a.type} Params: {a.parameters}")
        
    if len(parsed.actions) == 1 and parsed.actions[0].type == ActionType.WAIT:
        print("Parser returned WAIT (default). Parsing failed silently?")

    # assert len(parsed.actions) == 2
    assert parsed.actions[0].type == ActionType.PROPOSE_ALLIANCE
    assert parsed.actions[0].parameters["target"] == "p2"
    assert parsed.actions[0].parameters["duration"] == 5
    
    assert parsed.actions[1].type == ActionType.INITIATE_BUYOUT
    assert parsed.actions[1].parameters["target"] == "p3"
    assert parsed.actions[1].parameters["offer"] == 5000.0

if __name__ == "__main__":
    test_parser()
    print("Parser test passed!")
