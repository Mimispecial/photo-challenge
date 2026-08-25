from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "photo_challenge.py"
SDK = "v0.2.16"
PROMPT = "Compare two declared photo-challenge entries"


def address(account):
    return "0x" + account.hex()


def duel(vm, direct_deploy, host_left, right, judge):
    vm.sender = host_left
    contract = direct_deploy(
        str(CONTRACT), address(judge), address(host_left), address(right), "Neighborhood geometry",
        "Describe a photo showing one repeated geometric pattern and one visible source of natural light in a public place.",
        "Each entrant declares when and where the image was made; the contract records but does not authenticate that declaration.", sdk_version=SDK,
    )
    contract.append_criterion("The description explicitly identifies a repeated geometric pattern.")
    contract.append_criterion("The description explicitly identifies a visible source of natural light.")
    contract.open_duel()
    contract.submit_left_entry(
        "Repeating triangular roof braces cross the public market arcade while late-afternoon sunlight enters through an open skylight.",
        "The left entrant declares making the image at the public market arcade on 2026-08-20.",
    )
    vm.sender = right
    contract.submit_right_entry(
        "A single rectangular sign hangs inside the station concourse beneath electric ceiling lamps.",
        "The right entrant declares making the image at the public station concourse on 2026-08-20.",
    )
    vm.sender = host_left
    contract.freeze_entries()
    return contract


def test_declared_comparison_objection_and_human_judgment(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = duel(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"left_mask": "11", "right_mask": "00", "comparison": "LEFT"}))
    contract.compare_entries()
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True
    contract.object_left("The left entrant asks the judge to confirm that the declared market arcade is treated as a public place.")
    direct_vm.sender = direct_charlie
    contract.record_judgment("LEFT", "The human judge reviewed the frozen declarations and objection and selected the left entry.")
    assert contract.get_state()["final_winner"] == "LEFT"
    assert contract.get_entry("LEFT")["criterion_mask"] == "11"


def test_right_entrant_controls_right_objection(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = duel(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"left_mask": "11", "right_mask": "10", "comparison": "LEFT"}))
    contract.compare_entries()
    direct_vm.sender = direct_bob
    contract.object_right("The right entrant objects that the station description includes a repeated window grid not stated in the initial summary.")
    assert "window grid" in contract.get_entry("RIGHT")["objection"]
    with direct_vm.expect_revert("right_objection_unavailable"):
        contract.object_right("A second objection from the same side must not be accepted.")


def test_entry_roles_and_invalid_masks_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = duel(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.mock_llm(PROMPT, json.dumps({"left_mask": "111", "right_mask": "00", "comparison": "LEFT"}))
    with direct_vm.expect_revert("invalid_masks"):
        contract.compare_entries()
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only_judge"):
        contract.record_judgment("RIGHT", "An entrant cannot replace the independently designated human judge.")
    assert contract.get_state()["status"] == "READY_TO_COMPARE"
