<?php
// Synthetic component harness. The script block below is extracted byte-for-byte
// from the pinned portal/portal_payment.php revision named in case-manifest.json.
$GLOBALS['gateway_public_key'] = getenv('DEMO_PUBLIC');
$GLOBALS['gateway_api_key'] = getenv('DEMO_PRIVATE');
$GLOBALS['payment_gateway'] = getenv('DEMO_GATEWAY') ?: 'Stripe';
if (!$GLOBALS['gateway_public_key'] || !$GLOBALS['gateway_api_key']) {
    fwrite(STDERR, "Synthetic gateway configuration missing\n");
    exit(2);
}
function xl($value) { return $value; }
?>
    <script type="text/javascript">
        var chargeMsg = <?php $amsg = xl('Payment was successfully authorized and your card is charged.') . "\n" .
                xl("You will be notified when your payment is applied for this invoice.") . "\n" .
                xl('Until then you will continue to see payment details here.') . "\n" . xl('Thank You.');
            echo json_encode($amsg); // backward compatable 5.0.1
            ?>;
        var publicKey = <?php echo json_encode($GLOBALS['gateway_public_key']); ?>;
        var apiKey = <?php echo json_encode($GLOBALS['gateway_api_key']); ?>;

    </script>
<?php if ($GLOBALS['payment_gateway'] == 'AuthorizeNet') {
        // Include Authorize.Net dependency to tokenize card.
        // Will return a token to use for payment request keeping
        // credit info off the server.
        ?>
        <script type="text/javascript">
            function sendPaymentDataToAnet(e) {
                e.preventDefault();
                const authData = {};
                authData.clientKey = publicKey;
                authData.apiLoginID = apiKey;

                const cardData = {};
                cardData.cardNumber = document.getElementById("cardNumber").value;
                cardData.month = document.getElementById("expMonth").value;
                cardData.year = document.getElementById("expYear").value;
                cardData.cardCode = document.getElementById("cardCode").value;
                cardData.fullName = document.getElementById("cardHolderName").value;
                cardData.zip = document.getElementById("cczip").value;

                const secureData = {};
                secureData.authData = authData;
                secureData.cardData = cardData;

                Accept.dispatchData(secureData, acceptResponseHandler);

                function acceptResponseHandler(response) {
                    if (response.messages.resultCode === "Error") {
                        let i = 0;
                        while (i < response.messages.message.length) {
                            console.log(
                                response.messages.message[i].code + ": " +
                                response.messages.message[i].text
                            );
                            i = i + 1;
                        }
                    } else {
                        paymentFormUpdate(response.opaqueData);
                    }
                }
            }

            function paymentFormUpdate(opaqueData) {
                // this is card tokenized
                document.getElementById("dataDescriptor").value = opaqueData.dataDescriptor;
                document.getElementById("dataValue").value = opaqueData.dataValue;
                let oForm = document.forms['paymentForm'];
                oForm.elements['mode'].value = "AuthorizeNet";
                let inv_values = JSON.stringify(getFormObj('invoiceForm'));
                document.getElementById("invValues").value = inv_values;

                // empty out the fields before submitting to server.
                document.getElementById("cardNumber").value = "";
                document.getElementById("expMonth").value = "";
                document.getElementById("expYear").value = "";
                document.getElementById("cardCode").value = "";

                // Submit payment to server
                fetch('./lib/paylib.php', {
                    method: 'POST',
                    body: new FormData(oForm)
                }).then(function(response) {
                    if (!response.ok) {
                        throw Error(response.statusText);
                    }
                    return response.text();
                }).then(function(data) {
                    if(data !== 'ok') {
                        alert(data);
                        return;
                    }
                    alert(chargeMsg);
                    window.location.reload(false);
                }).catch(function(error) {
                    alert(error)
                });
            }
        </script>
    <?php }  // end authorize.net ?>
