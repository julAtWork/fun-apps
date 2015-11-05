/* This file is included both in funsite and edx-platorm/lms */

(function() {
    /* select current page menu item */
    var page = window.location.pathname.split('/')[1];
    $('#sandwich-overlay [data-location="'+ page +'"]').addClass('selected');

    /* Handle FUN overlays closing by clicking X */
    $('.close-overlay').on('click', function(event) {
        $('div.sequence-nav').css('z-index', 'auto');
        $(this).closest('.overlay').slideUp();
    });

    // Handle FUN overlays closing by hiting escape
    $(document).keydown(function(event) {
        if (event.keyCode == 27) { // ESC key
	    if ($('#sandwich-overlay').is(':visible')) {
		toggleSandwichMenu();
	    }
	    else{
		$('.hide-on-escape-key:visible').hide();
	    }
        }
    });

    /* Sandwich menu*/
    $('#sandwich-menu-icon').on('click', function(event) {
	toggleSandwichMenu();
    });

    function toggleSandwichMenu() {
	$('#sandwich-menu-icon').toggleClass('open');
	$('#sandwich-overlay').slideToggle(250);
    }

    /* Dropdown menu */
    $('#top-menu .right-nav .toggle-dropdown-menu').on('click', toggleDropdown);

     $('body').click(function() {
     	if ($('#top-menu .fun-dropdown-menu').is(":visible")) {
     	    $('#top-menu .fun-dropdown-menu').slideUp();
     	    toggleAccessiblePopUpAria(false);
     	}
     });

    function toggleDropdown(event) {
        if ($('#top-menu .fun-dropdown-menu').is(":hidden")) {
            $('#top-menu .fun-dropdown-menu').slideDown(100);
	    $('#top-menu .fun-dropdown-menu').show();
            toggleAccessiblePopUpAria(true);
        }
        else {
            $('#top-menu .fun-dropdown-menu').hide();
            toggleAccessiblePopUpAria(false);
        }
        event.preventDefault();
        event.stopPropagation();
    }

    function toggleAccessiblePopUpAria(display) {
        // aria-haspopup is used to improve accessibility.
        $('#top-menu .right-nav .toggle-dropdown-menu').attr('aria-haspopup', display);
    }
 })();
