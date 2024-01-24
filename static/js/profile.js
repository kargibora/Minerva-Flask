
document.querySelector('.profile-pic-container').addEventListener('click', function() {
    document.getElementById('profilePhotoUpload').click();
});

document.getElementById('profilePhotoUpload').addEventListener('change', function(event) {
    // Get the selected file
    var file = event.target.files[0];

    console.log(file)
    // Create a FormData object
    var formData = new FormData();
    formData.append('image', file);
    // Use the Fetch API to send the file
    fetch('/v1/api/upload-profile-picture', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Update the profile picture with the new URL
        document.getElementById('profilePicture').src = data.file_url;

    })
    .catch(error => {
        console.error('Error:', error);
    });
});