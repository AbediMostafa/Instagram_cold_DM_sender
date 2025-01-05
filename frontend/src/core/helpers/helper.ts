import {ElMessage} from "element-plus";
import Swal from "sweetalert2/dist/sweetalert2.js";

const copyToClipboard = (text) => {
    try {
        // Create a temporary input element
        const tempInput = document.createElement('input');
        tempInput.value = text;

        // Append it to the body
        document.body.appendChild(tempInput);

        // Select the text
        tempInput.select();
        tempInput.setSelectionRange(0, 99999); // For mobile devices

        // Execute the copy command
        document.execCommand('copy');

        // Remove the temporary input
        document.body.removeChild(tempInput);

        // Show success message
        ElMessage.success('Copied to clipboard!');
    } catch (err) {
        // Handle errors
        ElMessage.error('Failed to copy text');
        console.error('Failed to copy text: ', err);
    }
}

const getImageSrc = (src) => {
    return import.meta.env.VITE_APP_API_URL + '/storage/' + src
}

const cutMorThanNCharacters = (text, desiredLength) =>
    text && text.length > desiredLength ? text.substring(0, desiredLength) + ' ... ' : text;

const warningPromise = (text, body='') =>
    new Promise(resolve =>
        Swal.fire({
            title: text,
            icon: 'warning',
            text:body,
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: 'Yes!',
        }).then((result) => {
            if (result.isConfirmed) {
                resolve(result)
            }
        })
    )

export {
    getImageSrc,
    warningPromise,
    copyToClipboard,
    cutMorThanNCharacters,
};
