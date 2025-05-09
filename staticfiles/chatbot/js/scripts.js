const heroSection = document.querySelector('.hero');
const aboutUsSection = document.querySelector('.about-us');
const thirdPageSection = document.querySelector('.third-page');
const fourthPageSection = document.querySelector('.fourth-page');
const fifthPageSection = document.querySelector('.fifth-page'); // Select the fifth page

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    } else {
      entry.target.classList.remove('visible');
    }
  });
}, { threshold: 0.5 });

observer.observe(heroSection);
observer.observe(aboutUsSection);
observer.observe(thirdPageSection);
observer.observe(fourthPageSection);
observer.observe(fifthPageSection); // Observe the fifth page

function openPopup() {
  document.getElementById("popup").classList.add("open");
}

// Close the popup
function closePopup() {
  document.getElementById("popup").classList.remove("open");
}

