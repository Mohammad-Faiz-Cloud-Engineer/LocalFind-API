from fastapi import APIRouter

router = APIRouter(prefix="/donation", tags=["Donation"])

DONATION_CONFIG = {
    "upiId": "faiz2k9@fam",
    "payeeName": "Mohammad Faiz",
    "currency": "INR",
    "upiDeepLink": "upi://pay?pa=faiz2k9@fam&pn=Mohammad%20Faiz&cu=INR",
    "message": "Support LocalFind! Donate via UPI to help us keep the platform running.",
}


@router.get("")
async def donation_info():
    return {
        **DONATION_CONFIG,
        "note": "Scan or use the UPI deep link to make a donation.",
    }


@router.get("/link")
async def donation_link(amount: int | None = None):
    link = DONATION_CONFIG["upiDeepLink"]
    if amount and amount > 0:
        link = f"upi://pay?pa=faiz2k9@fam&pn=Mohammad%20Faiz&am={amount}&cu=INR"
    return {
        "upiId": DONATION_CONFIG["upiId"],
        "deepLink": link,
        "amount": amount,
    }
