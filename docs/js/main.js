const darkThemeMq = window.matchMedia("(prefers-color-scheme: dark)");

const themeBtn = document.getElementById('theme-toggle');
const root = document.documentElement;

if(!sessionStorage.getItem("theme")){
	sessionStorage.setItem("theme", "system");
	console.log("System theme");
}

if(sessionStorage.getItem("theme") == "system") setSystemTheme();
else if(sessionStorage.getItem("theme") == "light") setLightTheme();
else if(sessionStorage.getItem("theme") == "dark") setDarkTheme();

function setSystemTheme(){
    if(darkThemeMq.matches){
        setDarkTheme();
    }else{
        setLightTheme();
    }
}

function setDarkTheme(){
	root.setAttribute('data-theme', 'dark');
}

function setLightTheme() {
	root.removeAttribute('data-theme');
}

darkThemeMq.addListener(e => {
    if(sessionStorage.getItem("theme") == "system"){
        if (e.matches) {
            setDarkTheme();
        } else {
            setLightTheme();
        }
    }
});

function setTheme(){
    if(sessionStorage.getItem("theme") == "system"){
        sessionStorage.setItem("theme", "light");
        setLightTheme();
        console.log("Light theme");
    }else if(sessionStorage.getItem("theme") == "light"){
        sessionStorage.setItem("theme", "dark");
        setDarkTheme();
        console.log("Dark theme");
    }else{
        sessionStorage.setItem("theme", "system");
        setSystemTheme();
        console.log("System theme");
    }
}

themeBtn.addEventListener('click', () => {
	setTheme();
});

// Lightbox functionality for images
function createLightbox() {
	const lightbox = document.createElement('div');
	lightbox.className = 'image-lightbox';
	lightbox.id = 'lightbox';

	const closeBtn = document.createElement('span');
	closeBtn.className = 'lightbox-close';
	closeBtn.innerHTML = '&times;';
	closeBtn.setAttribute('aria-label', 'Close image');

	const img = document.createElement('img');
	img.className = 'lightbox-image';
	img.id = 'lightbox-img';

	lightbox.appendChild(closeBtn);
	lightbox.appendChild(img);
	document.body.appendChild(lightbox);

	return { lightbox, closeBtn, img };
}

const { lightbox, closeBtn, img } = createLightbox();

// Open lightbox when clicking on an image (single or in collage)
document.addEventListener('click', (e) => {
	if (e.target.tagName === 'IMG') {
		const wrapper = e.target.closest('.image-wrapper, .image-collage');
		if (wrapper) {
			img.src = e.target.src;
			img.alt = e.target.alt || '';
			lightbox.classList.add('active');
		}
	}
});

// Close lightbox on X button click or Escape key press
closeBtn.addEventListener('click', () => {
	lightbox.classList.remove('active');
});

document.addEventListener('keydown', (e) => {
	if (e.key === 'Escape' && lightbox.classList.contains('active')) {
		lightbox.classList.remove('active');
	}
});

// Close on background click (outside image)
lightbox.addEventListener('click', (e) => {
	if (e.target === lightbox && !e.target.classList.contains('lightbox-image')) {
		lightbox.classList.remove('active');
	}
});
