from pathlib import Path
import json

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Compare two declared photo-challenge entries"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"left_mask": "11", "right_mask": "00", "comparison": "LEFT"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_declared_photo_duel():
    host_left_account, right_account, judge_account = create_accounts(3)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "photo_challenge.py")
    deployed = factory.deploy_contract_tx(args=[judge_account.address, host_left_account.address, right_account.address, "Neighborhood geometry", "Describe a photo showing a repeated geometric pattern and a visible natural-light source in a public place.", "Each entrant declares when and where the image was made; the contract records but does not authenticate it."], account=host_left_account, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    host_left = factory.build_contract(address, account=host_left_account)
    right = factory.build_contract(address, account=right_account)
    judge = factory.build_contract(address, account=judge_account)
    ok(host_left.append_criterion(args=["The description explicitly identifies a repeated geometric pattern."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.append_criterion(args=["The description explicitly identifies a visible source of natural light."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.open_duel(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.submit_left_entry(args=["Repeating triangular roof braces cross the public market arcade while sunlight enters through a skylight.", "The left entrant declares making the image at the public market arcade on 2026-08-20."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(right.submit_right_entry(args=["A single rectangular sign hangs inside the station beneath electric ceiling lamps.", "The right entrant declares making the image at the public station on 2026-08-20."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.freeze_entries(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(host_left.compare_entries(args=[]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(judge.record_judgment(args=["LEFT", "The human judge reviewed the frozen declarations and selected the left entry."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert host_left.get_state(args=[]).call()["final_winner"] == "LEFT"
