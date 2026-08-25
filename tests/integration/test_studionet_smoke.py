import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address


def ok(receipt):
    assert tx_execution_succeeded(receipt)
    assert receipt.get("status_name") == TransactionStatus.FINALIZED.value
    assert receipt.get("result_name") in (None, "AGREE", "MAJORITY_AGREE")
    assert receipt.get("tx_execution_result_name") in (None, "FINISHED_WITH_RETURN")
    return receipt


@pytest.mark.integration
def test_studionet_photo_duel(default_account, secondary_account, tertiary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "photo_challenge.py")
    deployed = ok(factory.deploy_contract_tx(args=[tertiary_account.address, default_account.address, secondary_account.address, "Neighborhood geometry", "Describe a photo showing a repeated geometric pattern and a visible natural-light source in a public place.", "Each entrant declares when and where the image was made; the contract records but does not authenticate it."], account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    host_left = factory.build_contract(address, account=default_account)
    right = factory.build_contract(address, account=secondary_account)
    ok(host_left.append_criterion(args=["The description explicitly identifies a repeated geometric pattern."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.append_criterion(args=["The description explicitly identifies a visible source of natural light."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.open_duel(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.submit_left_entry(args=["Repeating triangular roof braces cross the public market arcade while sunlight enters through a skylight.", "The left entrant declares making the image at the public market arcade on 2026-08-20."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(right.submit_right_entry(args=["A single rectangular sign hangs inside the station beneath electric ceiling lamps.", "The right entrant declares making the image at the public station on 2026-08-20."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.freeze_entries(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = ok(host_left.compare_entries(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    state = host_left.get_state(args=[]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["status"] == "OBJECTION_WINDOW"
    assert state["comparison"] in ("LEFT", "RIGHT", "TIE", "NEITHER")
    observed = state["comparison"]
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": observed}, sort_keys=True))
