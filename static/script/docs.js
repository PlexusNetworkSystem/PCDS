if (typeof NodeList.prototype.forEach === 'undefined') {
    // Polyfill for nodelist foreach for ie11
    NodeList.prototype.forEach = function (callback, scope) {
        for (var i = 0; i < this.length; i++) {
            callback.call(scope, this[i], i); // passes back stuff we need
        }
    };
}

// Cross browser friendly matches
const matches = function (el, selector) {
    return (el.matches || el.matchesSelector || el.msMatchesSelector || el.mozMatchesSelector || el.webkitMatchesSelector || el.oMatchesSelector).call(el, selector);
};

// Get the dom element's children
const getChildren = function (el, selector) {
    return [].some.call(el.children, function (e) {
        return matches(e, selector);
    });
};

// Decode html encoded elements
const htmlDecode = function (input) {
    let e = document.createElement('div');
    e.innerHTML = input;
    return e.childNodes[0].nodeValue;
};

// Open and close the sidebar
document.querySelector('.sidebar-toggle').addEventListener('click', function (e) {
    document.querySelector('.sidebar').classList.toggle('side-bar-closed');
    return false;
});

// Open and close the navlinks
let navlinks = document.querySelectorAll('.sidebar ul a');
navlinks.forEach(function (link) {
    // Remove links that have children and add the class to the li wrapper
    if (getChildren(link.parentNode, 'ul')) {
        link.parentNode.classList.add('has-children');
        link.setAttribute('tabindex', '-1');
    }

    link.addEventListener('click', function (e) {
        if (getChildren(link.parentNode, 'ul')) {
            e.preventDefault();

            link.parentNode.classList.toggle('active');
            link.parentNode.querySelectorAll('.active').forEach(function (active) {
                active.classList.toggle('active');
            });

            return false;
        }
    });
});

// Markdown parser using
// https://github.com/showdownjs/showdown
let parser = new showdown.Converter();
parser.setFlavor('github');
parser.setOption('ghCompatibleHeaderId', true);
parser.setOption('prefixHeaderId', false);

// Parse the markdown on the page
let markdown = document.querySelectorAll('.markdown');
markdown.forEach(function (m) {
    // Remove spaces for easier layout.... wouldn't be like this in an actual app
    // something like <div class="markdown">{{ $markdown }}</div> for laravel
    let code = m.innerHTML.replace(/^\s+\r?\n|\r?\n\s+$/g, '');
    let spaces = Math.min.apply(null, code.match(/^ +/gm).map(s => s.length));
    let unindented = code.replace(new RegExp("^ {" + spaces + "}", "gm"), '');

    // Also need to decode for blockquote syntax
    let preformat = htmlDecode(unindented);

    m.innerHTML = parser.makeHtml(preformat);

    // Add data-title attribute for relevant items in table after parsing
    let tables = m.querySelectorAll('table');
    tables.forEach(function (table) {
        let headers = table.querySelectorAll('thead th');
        let rows = table.querySelectorAll('tbody tr');
        rows.forEach(function (row) {
            let cells = row.querySelectorAll('td, th');

            cells.forEach(function (cell, index) {
                cell.setAttribute('data-title', headers[index].innerText);
            });
        });
    });

    // Add styling to code blocks
    let codeBlocks = m.querySelectorAll('pre code');
    codeBlocks.forEach(function (codeBlock) {
        hljs.highlightBlock(codeBlock);
    });
});