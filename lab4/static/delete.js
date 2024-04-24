let deleteUserModal = document.querySelector('#staticBackdrop');

deleteUserModal.addEventListener('show.bs.modal', function(event){
    let button = event.relatedTarget;
    console.log(button)
    let userId = button.dataset.id;

    console.log(userId)
    let userName = document.querySelector(".username").textContent
    console.log(userName)
    let deleteButton = document.querySelector('#deleteButton');
    let userLogin = deleteUserModal.querySelector('.name-user');

    // Устанавливаем атрибут href для ссылки на кнопке "Удалить"
    deleteButton.href = `/delete/${userId}`;

    // Устанавливаем имя пользователя в модальное окно
    userLogin.textContent = userName;
});