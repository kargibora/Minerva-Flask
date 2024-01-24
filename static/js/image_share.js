


$(document).ready(function () {
    let images = [];
    let imageUrl;
    let imageId;

    let selectedImageUrl;
    let selectedImageDescription;

    // Fetch the images from the server
    function fetchUserImages(username) {
        $.ajax({
            url: `/v1/api/get-artworks/${username}`,
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                images = data.map(item => ({
                    url: item.imageURLS3,
                    description: item.generativeCaption,
                    _id : item._id
                }));
                initImagePicker();
            },
            error: function () {
                alert('Error fetching images. Please try again later.');
            },
        });
    }

    function getImageFile(url) {
        return fetch('http://127.0.0.1:5000/v1/api/get-image-file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        })
        .then(response => response.blob())
        .then(blob => new File([blob], "filename.png", { type: 'image/png' }))
        .catch(error => console.error('Error:', error));
    }
    
    async function uploadImage() {
        const imageUrl = $('#selected-image').attr('src');
    
        // Fetch image data from URL
        let imageFile = await getImageFile(imageUrl);
    
        // Create a FormData instance
        var formData = new FormData();
        formData.append('file', imageFile);
        formData.append('text_prompt', selectedImageDescription);
        formData.append('username', username);
        // Send the request
        $.ajax({
            url: 'http://127.0.0.1:5000/v1/api/upload-image',
            method: 'POST',
            processData: false, // Important!
            contentType: false, // Important!
            data: formData,
            success: function() {
                alert('Image has been saved successfully!');
            },
            error: function() {
                alert('Error saving the image. Please try again later.');
            },
        });
    }

    function initImagePicker() {
        const userId = 1;

       
    function showImagePicker() {
        const imagePicker = document.createElement('div');
        imagePicker.className = 'image-picker';
        const overlay = document.createElement('div');
        overlay.className = 'overlay';

        const searchBar = document.createElement('input');
        searchBar.type = 'text';
        searchBar.placeholder = 'Search images by description';
        searchBar.className = 'search-bar bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500';


        searchBar.addEventListener('keyup', filterImages);
        searchBar.style.width = '100%';

        overlay.addEventListener('click', function () {
            overlay.remove();
            imagePicker.remove();
        });

        document.body.appendChild(overlay);
        document.body.appendChild(imagePicker);
        imagePicker.appendChild(searchBar);

        // Function to filter images based on search
        function filterImages(e) {
            const searchTerm = e.target.value.toLowerCase();
            const filteredImages = images.filter(image => image.description.toLowerCase().includes(searchTerm));
            renderImages(filteredImages);
        }

        // Function to render images to the picker
        function renderImages(imageArray) {
            // Clear the image picker content but leave the search bar
            while (imagePicker.children.length > 1) {
                imagePicker.removeChild(imagePicker.lastChild);
            }

            // Add your images to the imagePicker
            imageArray.forEach((image, index) => {
                const img = document.createElement('img');
                img.src = image.url;
                img.alt = 'Image ' + (index + 1);
                img.addEventListener('click', function () {
                    imageUrl = image.url;
                    imageId = image._id;
                    console.log(imageUrl);
                    $('#selected-image').attr('src', imageUrl);

                    selectedImageDescription = image.description;
                    selectedImageUrl = image.url;
                    setSelectedArtworkId(image._id);

                    overlay.remove();
                    imagePicker.remove();
                });
                imagePicker.appendChild(img);
            });
        }

        // Initial render of all images
        renderImages(images);
    }

        function shareToEvent(description, imageUrl, imageId, eventId) {
            console.log(description, imageUrl, imageId, eventId);

                $.ajax({
                    url: '/v1/api/share-post/event',
                    method: 'POST',
                    contentType: 'application/json', // Set the content type as JSON
                    processData: false, // Don't process the data as a query string
                    data: JSON.stringify({ // Convert the data object to a JSON string
                        description: description,
                        image_url: imageUrl,
                        image_id: imageId,
                        event_id: eventId,
                    }),
                    beforeSend: function () {
                        $('.spinner').show();
                    },
                    success: function () {
                        $('.spinner').hide();
                        $('.success').show();
                        setTimeout(function () {
                            $('.success').hide();
                        }, 3000);

                        $('#success-message').text('Image has been shared successfully!');
                        $('#success-message').show().delay(5000).fadeOut();

                        // get the post id from response
                        const post_id = response._id;
                        window.location.href = '/p/' + post_id;


                    },
                    error: function (xhr, status, error) {
                        $('.spinner').hide();
                        alert('Error sharing the image. Please try again later. ' + error);
                    },
                });
        }

        function shareToProfile(description, imageUrl, imageId) {
            $.ajax({
                url: '/v1/api/share-post',
                method: 'POST',
                contentType: 'application/json', // Set the content type as JSON
                processData: false, // Don't process the data as a query string
                data: JSON.stringify({ // Convert the data object to a JSON string
                    description: description,
                    image_url: imageUrl,
                    image_id: imageId,
                }),
                beforeSend: function () {
                    $('.spinner').show();
                },
                success: function () {
                    $('.spinner').hide();
                    $('.success').show();
                    setTimeout(function () {
                        $('.success').hide();
                    }, 3000);

                    $('#success-message').text('Image has been shared successfully!');
                    $('#success-message').show().delay(5000).fadeOut();

                    // get the post id from response
                    const post_id = response._id;
                    window.location.href = '/p/' + post_id;


                },
                error: function (xhr, status, error) {
                    $('.spinner').hide();
                    alert('Error sharing the image. Please try again later. ' + error);
                },
            });
        }
        // Attach event listeners
        $('.change-image').on('click', showImagePicker);
        $('#image-container').on('click', showImagePicker);

        $('#share-to-profile-btn').on('click', function (event) {
            event.preventDefault();
            const description = $('#description').val();

            // check which checkbox is selected
            const isProfile = $('#share-on-profile').is(':checked');
            const isEvent = $('#share-on-event').is(':checked');

            if (isProfile) {
                shareToProfile(description, imageUrl, imageId);
            }
            if (isEvent) {
                // get which event is selected
                let selectElement = document.getElementById('event_multiple');
                let selectedOption = selectElement.value;
                shareToEvent(description, imageUrl, imageId, selectedOption);
            }
        });
    }

    $('#save-image').on('click', function() {
        uploadImage().then(() => console.log('Image upload completed.')).catch(e => console.error(e));
    });

    


    // Call fetchUserImages to fetch the images and initialize the image picker
    fetchUserImages(username);


});

// Function to apply effects
function applyEffects() {
    let saturation = $('#saturation-slider').val();
    let hue = $('#hue-slider').val();
    let brightness = $('#brightness-slider').val();
    let contrast = $('#contrast-slider').val();
    let blur = $('#blur-slider').val();
    let sepia = $('#sepia-slider').val();
    let invert = $('#invert-slider').val();


    // Convert the slider values to proper CSS filter values
    saturation = saturation / 50;
    hue = hue * 3.6;
    brightness = brightness / 50;
    contrast = contrast / 100;
    blur = blur + 'px';
    sepia = sepia + '%';
    invert = invert + '%';

    // Apply the CSS filter property to the image
    $('#selected-image').css('filter', `hue-rotate(${hue}deg) saturate(${saturation}) brightness(${brightness}) contrast(${contrast}) blur(${blur}) sepia(${sepia}) invert(${invert})`);
}

$(document).ready(function() {
    $('.effect-button').click(function() {
        const sliderId = $(this).attr('id').replace('-button', '-slider');
        $('#' + sliderId).toggle();
    });

    $('.slider').on('input', function() {
        const effectName = $(this).attr('id').replace('-slider', '');
        const value = $(this).val();
        applyEffect(effectName, value);
    });
});


$('#toggle-effects-panel').on('click', function (event) {
    event.preventDefault();
    const effectPanel = $('#effect-panel');
    effectPanel.toggleClass('hidden');

    // Change button text based on the panel state
    $(this).text(effectPanel.hasClass('closed') ? ' > ' : ' < ');
});

$('#open-effects').on('click', function () {
    const effectPanel = $('#effect-panel');
    effectPanel.toggleClass('closed');

    // Change button symbol based on the panel state
    $('#toggle-effects-panel').text(effectPanel.hasClass('closed') ? ' > ' : ' < ');
});

$('#close-panel').on('click', function (event) {
    event.preventDefault();
    $('#effect-panel').addClass('hidden');
    $('#toggle-effects-panel').text('Open Effects');
});

// Event listeners for the sliders
$('#saturation-slider').on('input', applyEffects);
$('#hue-slider').on('input', applyEffects);
$('#brightness-slider').on('input', applyEffects);
$('#contrast-slider').on('input', applyEffects);
$('#blur-slider').on('input', applyEffects);
$('#sepia-slider').on('input', applyEffects);
$('#invert-slider').on('input', applyEffects);
$('#reset-button').on('click', function(event) {
    // Reset the slider values
    event.preventDefault();
    $('#saturation-slider').val(50);
    $('#hue-slider').val(0);
    $('#brightness-slider').val(50);
    $('#contrast-slider').val(100);
    $('#blur-slider').val(0);
    $('#sepia-slider').val(0);
    $('#invert-slider').val(0);

    // Reapply the effects
    applyEffects();
});

// Get all slider elements
var sliders = document.querySelectorAll('.slider');

// For each slider
sliders.forEach(function(slider) {
    // Update CSS variable when the slider value changes
    slider.oninput = function() {
        // Calculate percentage
        var value = (this.value-this.min)/(this.max-this.min)*100
        // Update CSS variable
        this.style.setProperty('--value', value + '%');
    }

    // Trigger the oninput event manually
    slider.dispatchEvent(new Event('input'));
});


// Event listener for the "Open Effects" button
$('#open-effects').on('click', function() {
    $('#effect-container').toggle();
});
