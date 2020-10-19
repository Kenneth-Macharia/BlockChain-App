// Section selection on side bar button click
$(".dash").click(function (e) {
    e.preventDefault();
    sectionDisplay('dash');
});

$(".find").click(function (e) {
    e.preventDefault();
    sectionDisplay('find');
});

$(".add").click(function (e) {
    e.preventDefault();
    sectionDisplay('add');
});

// Section selection on app routing
var sectionParam = window.location.pathname.replace('/', '');
switch (sectionParam) {
    case '':
        sectionDisplay('dash');
        break;

    case 'find':
        sectionDisplay('find');
        break;

    case 'add':
        sectionDisplay('add');
        break;
}

// if (sectionParam === 'add') {
//     sectionDisplay('add');
// } else if (sectionParam == 'find') {
//     sectionDisplay('find')
// } else {
//     sectionDisplay('dash');
// }

// Add section county & location drop-down options
$("#county").change(function (e) {
    switch (this.value) {
        case 'Nairobi':
            $("#location").find('option').remove().end();
            $("#location").append(new Option('Choose...', ''));
            $("#location").append(new Option('Dagoretti', 'Dagoretti'));
            $("#location").append(new Option('Kangemi', 'Kangemi'));
            $("#location").append(new Option('Langata', 'Langata'));
            break;

        case 'Kiambu':
            $("#location").find('option').remove().end();
            $("#location").append(new Option('Choose...', ''));
            $("#location").append(new Option('Kikuyu', 'Kikuyu'));
            $("#location").append(new Option('Thika', 'Thika'));
            $("#location").append(new Option('Limuru', 'Limuru'));
            break;

        case 'Nyeri':
            $("#location").find('option').remove().end();
            $("#location").append(new Option('Choose...', ''));
            $("#location").append(new Option('Othaya', 'Othaya'));
            $("#location").append(new Option('Karatina', 'Karatina'));
            $("#location").append(new Option('Mwiga', 'Mwiga'));
            break;
    }
});

function sectionDisplay(param) {
    titleMap = {
        'dash': 'Dashboard',
        'add': 'Add a record',
        'find': 'Find a record'
    };

    let sections = $(".container-fluid");

    for (section of sections) {
        if (section.getAttribute('id') === param) {
            $("#section-heading").html(titleMap[param]);
            section.style.display = 'block';

        } else {
            section.style.display = 'none';
        }
    }
}

// Side bar toogle
// $("#menu-toggle").click(function (e) {
//     e.preventDefault();
//     $("#wrapper").toggleClass("toggled");
// });
