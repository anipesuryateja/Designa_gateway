from pydoc import html
import httpx
import xml.etree.ElementTree as ET

WINCAVE_HIT_ENDPOINT = "https://windcave-hit-mock-api-bmf2drabc5esfub6.eastus-01.azurewebsites.net/hit/pos.aspx"

def optional_tag(tag, value):
    return f"<{tag}>{value}</{tag}>" if value else ""

async def send_hit_purchase_request(data: dict):
    """
    Builds XML, sends request to Windcave HIT mock endpoint,
    parses XML response, and returns JSON.
    """

    # Build the HIT XML request
    # xml_body = f"""
    # <Scr action="doScrHIT" user="{data['user']}" key="{data['key']}">
    #     <Amount>{data['amount']}</Amount>
    #     <Cur>{data['currency']}</Cur>
    #     <TxnType>Purchase</TxnType>
    #     <Station>{data['station']}</Station>
    #     <TxnRef>{data['txnRef']}</TxnRef>
    #     <DeviceId>{data['deviceId']}</DeviceId>
    #     <PosName>{data['posName']}</PosName>
    #     <PosVersion>{data['posVersion']}</PosVersion>
    #     <VendorId>{data['vendorId']}</VendorId>
    #     <MRef>{data['mref']}</MRef>
    # </Scr>
    # """.strip()

    xml_body = f"""
<Scr action="doScrHIT" user="{html.escape(data['user'])}" key="{html.escape(data['key'])}">
    <Amount>{data['amount']}</Amount>
    <Cur>{html.escape(data['currency'])}</Cur>
    <TxnType>Purchase</TxnType>
    <Station>{html.escape(data['station'])}</Station>
    <TxnRef>{html.escape(data['txnRef'])}</TxnRef>
    <DeviceId>{html.escape(data['deviceId'])}</DeviceId>
    {optional_tag("PosName", data.get("posName"))}
    {optional_tag("PosVersion", data.get("posVersion"))}
    {optional_tag("VendorId", data.get("vendorId"))}
    {optional_tag("MRef", data.get("mref"))}
</Scr>
""".strip()


    headers = {
        "Content-Type": "application/xml"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            WINCAVE_HIT_ENDPOINT,
            data=xml_body,
            headers=headers
        )

    # Parse the XML response from Windcave mock
    root = ET.fromstring(response.text)

    # Convert XML to JSON-like dict
    parsed = {child.tag: child.text for child in root}
    parsed["TxnType"] = "Purchase"
    return parsed




async def send_hit_refund_request(data: dict):
    xml_body = f"""
<Scr action="doScrHIT" user="{html.escape(data['user'])}" key="{html.escape(data['key'])}">
    <Amount>{data['amount']}</Amount>
    <Cur>{html.escape(data['currency'])}</Cur>
    <TxnType>Refund</TxnType>
    <Station>{html.escape(data['station'])}</Station>
    <TxnRef>{html.escape(data['txnRef'])}</TxnRef>
    <DpsTxnRef>{html.escape(data['dpsTxnRef'])}</DpsTxnRef>
    <DeviceId>{html.escape(data['deviceId'])}</DeviceId>
    <PosName>{html.escape(data['posName'])}</PosName>
    <VendorId>{html.escape(data['vendorId'])}</VendorId>
    <MRef>{html.escape(data['mref'])}</MRef>
</Scr>
""".strip()

    print("===== XML SENT TO WINCAVE =====")
    print(xml_body)
    print("================================")

    headers = {"Content-Type": "application/xml"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            WINCAVE_HIT_ENDPOINT,
            data=xml_body,
            headers=headers
        )

    print("===== RAW RESPONSE =====")
    print(response.text)
    print("========================")

    # Parse
    root = ET.fromstring(response.text)
    parsed = {child.tag: child.text for child in root}

    # Add TxnType manually
    parsed["TxnType"] = "Refund"
    parsed["DpsTxnRef"] = data["dpsTxnRef"]
    parsed["DeviceId"] = data["deviceId"]
    parsed["Station"] = data["station"]

    return parsed




async def send_hit_unmatched_refund_request(data: dict):

    xml_body = f"""
<Scr action="doScrHIT" user="{data['user']}" key="{data['key']}">
    <Amount>{data['amount']}</Amount>
    <Cur>{data['currency']}</Cur>
    <TxnType>Refund</TxnType>
    <Station>{data['station']}</Station>
    <TxnRef>{data['txnRef']}</TxnRef>
    <DeviceId>{data['deviceId']}</DeviceId>
    <PosName>{data['posName']}</PosName>
    <VendorId>{data['vendorId']}</VendorId>
    <MRef>{data['mref']}</MRef>
</Scr>
""".strip()

    print("===== XML SENT TO WINCAVE =====")
    print(xml_body)
    print("================================")

    headers = {"Content-Type": "application/xml"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            WINCAVE_HIT_ENDPOINT,
            data=xml_body,
            headers=headers
        )

    print("===== RAW RESPONSE =====")
    print(response.text)
    print("========================")

    root = ET.fromstring(response.text)
    parsed = {child.tag: child.text for child in root}

    # Add missing fields manually
    parsed["TxnType"] = "Refund"
    parsed["DeviceId"] = data["deviceId"]
    parsed["Station"] = data["station"]
    parsed["MRef"] = data["mref"]

    return parsed



async def send_hit_reversal_request(data: dict):

    xml_body = f"""
<Scr action="doScrHIT" user="{data['user']}" key="{data['key']}">
    <TxnType>Reversal</TxnType>
    <Station>{data['station']}</Station>
    <TxnRef>{data['txnRef']}</TxnRef>
</Scr>
""".strip()

    print("===== XML SENT TO WINCAVE =====")
    print(xml_body)
    print("================================")

    headers = {"Content-Type": "application/xml"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            WINCAVE_HIT_ENDPOINT,
            data=xml_body,
            headers=headers
        )

    print("===== RAW RESPONSE =====")
    print(response.text)
    print("========================")

    # Parse XML response
    root = ET.fromstring(response.text)
    parsed = {child.tag: child.text for child in root}

    # Add missing fields manually
    parsed["TxnType"] = "Reversal"
    parsed["TxnRef"] = data["txnRef"]
    parsed["Station"] = data["station"]

    return parsed



async def send_hit_status_request(data: dict):

    xml_body = f"""
<Scr action="doScrHIT" user="{data['user']}" key="{data['key']}">
    <TxnType>Status</TxnType>
    <Station>{data['station']}</Station>
    <TxnRef>{data['txnRef']}</TxnRef>
</Scr>
""".strip()

    print("===== XML SENT TO WINCAVE =====")
    print(xml_body)
    print("================================")

    headers = {"Content-Type": "application/xml"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            WINCAVE_HIT_ENDPOINT,
            data=xml_body,
            headers=headers
        )

    print("===== RAW RESPONSE =====")
    print(response.text)
    print("========================")

    # Parse XML response
    root = ET.fromstring(response.text)
    parsed = {child.tag: child.text for child in root}

    # Add missing fields manually
    parsed["TxnType"] = "Status"
    parsed["TxnRef"] = data["txnRef"]
    parsed["Station"] = data["station"]

    return parsed



# async def send_hit_receipt_request(data: dict, ):

#     xml_body = f"""
# <Scr action="doScrHIT" user="{data['user']}" key="{data['key']}">
#     <TxnType>Receipt</TxnType>
#     <Station>{data['station']}</Station>
#     <TxnRef>{data['txnRef']}</TxnRef>
#     <DuplicateFlag>{data.get('duplicateFlag', 0)}</DuplicateFlag>
#     <ReceiptType>{data['receiptType']}</ReceiptType>
# </Scr>
# """.strip()

#     print("===== XML SENT TO WINCAVE =====")
#     print(xml_body)
#     print("================================")

#     headers = {"Content-Type": "application/xml"}

#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.post(
#             WINCAVE_HIT_ENDPOINT,
#             data=xml_body,
#             headers=headers
#         )

#     print("===== RAW RESPONSE =====")
#     print(response.text)
#     print("========================")

#     # Parse XML response
#     root = ET.fromstring(response.text)
#     parsed = {child.tag: child.text for child in root}

#     # Add missing fields manually
#     parsed["TxnType"] = "Receipt"
#     parsed["TxnRef"] = data["txnRef"]
#     parsed["Station"] = data["station"]
#     parsed["DuplicateFlag"] = str(data.get("duplicateFlag", 0))
#     parsed["ReceiptType"] = str(data["receiptType"])

#     return parsed



async def send_hit_receipt_request(data: dict, action: str = None):
    # Build XML
    xml_body = f"""
<Scr action="doScrHIT" user="{html.escape(data['user'])}" key="{html.escape(data['key'])}">
    <Station>{html.escape(data['station'])}</Station>
    <TxnType>Receipt</TxnType>
    <TxnRef>{html.escape(data['txnRef'])}</TxnRef>
    <ReceiptType>{data['receiptType']}</ReceiptType>
    <DuplicateFlag>{data.get('duplicateFlag',0)}</DuplicateFlag>
"""
    if data.get("printer"):
        xml_body += f"    <Printer>{html.escape(data['printer'])}</Printer>\n"

    if action:
        xml_body += f"    <Action>{html.escape(action)}</Action>\n"

    xml_body += "</Scr>"

    print("===== XML SENT TO WINCAVE (Receipt) =====")
    print(xml_body)
    print("================================")

    headers = {"Content-Type": "application/xml"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(WINCAVE_HIT_ENDPOINT, data=xml_body, headers=headers)

    # Parse response
    try:
        root = ET.fromstring(response.text)
        parsed = {child.tag: child.text for child in root}
        parsed["TxnType"] = "Receipt"
        return parsed
    except ET.ParseError:
        print("❌ XML parsing failed!")
        return {"raw_response": response.text, "TxnType": "Receipt"}


async def send_hit_enterdata_request(data: dict):
    # Build XML
    xml_body = f"""
<Scr action="doScrHIT" user="{html.escape(data['user'])}" key="{html.escape(data['key'])}">
    <Station>{html.escape(data['station'])}</Station>
    <TxnType>EnterData</TxnType>
    <CmdSeq>{data['cmdSeq']}</CmdSeq>
    <PromptId>{data['promptId']}</PromptId>
    <Timeout>{data['timeout']}</Timeout>
</Scr>
""".strip()

    print("===== XML SENT TO WINCAVE (EnterData) =====")
    print(xml_body)
    print("================================")

    headers = {"Content-Type": "application/xml"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(WINCAVE_HIT_ENDPOINT, data=xml_body, headers=headers)

    # Parse response
    try:
        root = ET.fromstring(response.text)
        parsed = {child.tag: child.text for child in root}
        parsed["TxnType"] = "EnterData"
        return parsed
    except ET.ParseError:
        print("❌ XML parsing failed!")
        return {"raw_response": response.text, "TxnType": "EnterData"}
    


async def send_hit_generic_request(txn_type: str, data: dict):
    """
    Send generic HIT XML request for operations like PinpadDisplay, ReadCard, SettlementSummary, Ping.
    """
    xml_body = f'<Scr action="doScrHIT" user="{html.escape(data.get("user",""))}" key="{html.escape(data.get("key",""))}">'
    for key, value in data.items():
        if key not in ["user", "key"]:
            xml_body += f"<{key}>{html.escape(str(value))}</{key}>"
    xml_body += f"<TxnType>{txn_type}</TxnType></Scr>"

    print("===== XML SENT TO WINCAVE =====")
    print(xml_body)
    print("================================")

    headers = {"Content-Type": "application/xml"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            WINCAVE_HIT_ENDPOINT,
            data=xml_body,
            headers=headers
        )

    try:
        root = ET.fromstring(response.text)
        parsed = {child.tag: child.text for child in root}
    except ET.ParseError:
        # Return raw text if XML parsing fails
        parsed = {"raw_response": response.text}

    parsed["TxnType"] = txn_type
    return parsed



async def send_hit_ui_button_request(data: dict):
    """
    Send Windcave HIT UI button-press request.
    TxnType = UI
    UiType  = Bn
    Name    = B1 | B2
    Val     = YES | NO | CANCEL
    """

    # Validate values for safety
    name = data["name"]
    val = data["val"]

    if name not in ("B1", "B2"):
        raise ValueError("Invalid button name: must be B1 or B2")

    if val not in ("YES", "NO", "CANCEL"):
        raise ValueError("Invalid button val: must be YES, NO, CANCEL")
    

    xml_body = f"""
<Scr action="doScrHIT" user="{html.escape(data['user'])}" key="{html.escape(data['key'])}">
    <Station>{html.escape(data['station'])}</Station>
    <TxnType>UI</TxnType>
    <UiType>Bn</UiType>
    <Name>{html.escape(name)}</Name>
    <Val>{html.escape(val)}</Val>
    <TxnRef>{html.escape(data['txnRef'])}</TxnRef>
</Scr>
""".strip()

    print("===== XML SENT TO WINDCAVE (UI Button) =====")
    print(xml_body)
    print("============================================")

    headers = {"Content-Type": "application/xml"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            WINCAVE_HIT_ENDPOINT,
            data=xml_body,
            headers=headers
        )

    print("===== RAW RESPONSE =====")
    print(response.text)
    print("========================")

    # Parse XML
    try:
        root = ET.fromstring(response.text)
        parsed = {child.tag: child.text for child in root}
    except ET.ParseError:
        return {
            "TxnType": "UI",
            "error": "Failed to parse XML",
            "raw_response": response.text
        }

    parsed.update({
        "TxnType": "UI",
        "UiType": "Bn",
        "ButtonName": name,
        "ButtonValue": val,
        "Station": data["station"],
        "TxnRef": data["txnRef"]
    })

    return parsed
