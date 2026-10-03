const video = document.querySelector('#v');
for (const button of document.querySelectorAll('button[data-time]')) {
  button.addEventListener('click', () => {
    video.pause();
    video.currentTime = Number(button.dataset.time);
  });
}
