

$(document).ready(function(){
    
    // Add To Selection
    $(".add-to-selection").on("click", function(){

        let button = $(this)
        let id = button.attr("data-index")

        let hotel_id = $("#id").val()
        let room_id = $(`.room_id_${id}`).val()
        let room_number = $(`.room_number_${id}`).val()
        let hotel_name = $("#hotel_name").val()
        let room_name = $("#room_name").val()
        let room_price = $("#room_price").val()
        let number_of_beds = $("#number_of_beds").val()
        let room_type = $("#room_type").val()
        let room_capacity = $("#room_capacity").val()
        let checkin = $("#checkin").val()
        let checkout = $("#checkout").val()
        let adult = $("#adult").val()
        let children = $("#children").val()

        // Removed console.log statements for booking data debugging (security improvement)
        // Previously logged: id, hotel_id, room_number, room_id, hotel_name, room_name, 
        // room_price, number_of_beds, room_type, room_capacity, checkin, checkout, adult, children


        $.ajax({
            url:'/booking/add_to_selection/',
            data: {
                'id': id,
                'hotel_id': hotel_id,
                'hotel_name': hotel_name,
                'room_number': room_number,
                'room_name': room_name,
                'room_price': room_price,
                'number_of_beds': number_of_beds,
                'room_type': room_type,
                'room_id': room_id,
                'room_capacity': room_capacity,
                'checkin': checkin,
                'checkout': checkout,
                'adult': adult,
                'children': children,
            },
            dataType: 'json',
            beforeSend: function(){
                // Removed console.log for "Adding room..." status
                button.html("<i class='fas fa-clock-rotate-left'></i> " + gettext("Adding room...") + " ")
            },
            success: function(response){
                // Проверяем, есть ли ошибка с отелем
                if (response.error) {
                    // Показываем уведомление с возможностью очистить корзину
                    Swal.fire({
                        title: gettext('Attention!'),
                        text: response.message,
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonText: gettext('Yes, clear'),
                        cancelButtonText: gettext('No, cancel')
                    }).then((result) => {
                        if (result.isConfirmed) {
                            // Если пользователь согласился очистить корзину
                            $.ajax({
                                url: '/booking/clear_session_and_add_new/',
                                data: {
                                    'id': id,
                                    'hotel_id': hotel_id,
                                    'hotel_name': hotel_name,
                                    'room_number': room_number,
                                    'room_name': room_name,
                                    'room_price': room_price,
                                    'number_of_beds': number_of_beds,
                                    'room_type': room_type,
                                    'room_id': room_id,
                                    'room_capacity': room_capacity,
                                    'checkin': checkin,
                                    'checkout': checkout,
                                    'adult': adult,
                                    'children': children,
                                },
                                dataType: 'json',
                                success: function(res) {
                                    button.html("<i class='fas fa-check-circle'></i> " + gettext("Added to selection") + " ");

                                    
                                    const Toast = Swal.mixin({
                                        toast: true,
                                        position: 'top-end',
                                        showConfirmButton: false,
                                        timer: 1500,
                                        timerProgressBar: true,
                                    });

                                    Toast.fire({
                                        icon: 'success',
                                        title: gettext('Корзина очищена и добавлен новый номер')
                                    });
                                }
                            });
                        } else {
                            // Если пользователь отменил
                            button.html("<i class='fas fa-plus'></i> " + gettext("Add To Selection"));
                        }
                    });
                    return;
                }
                
                let buttonText = button.text().trim();
                
                // Определяем новый текст кнопки
                if (buttonText === gettext("Update") || buttonText === "Обновить") {
                    button.html("<i class='fas fa-check-circle'></i> " + gettext("Updated") + " ")
                } else {
                    button.html("<i class='fas fa-check-circle'></i> " + gettext("Added to selection") + " ")
                }


                
                // Загружаем и показываем новые messages после операции
                if (typeof loadAndDisplayMessages === 'function') {
                    setTimeout(loadAndDisplayMessages, 500); // Небольшая задержка для обработки
                }

                ;
                
                // const Toast = Swal.mixin({
                //     toast: true,
                //     position: 'top-end',
                //     showConfirmButton: false,
                //     timer: 1000,
                //     timerProgressBar: true,
                // })
                //
                // Toast.fire({
                //     icon: 'success',
                //     title: buttonText === "Update" || buttonText === "Обновить" ?
                //         'Room Updated Successfully!' : 'Added Room To Selection!'
                // })
            }
        })

    })

    // Delete item from cart
	$(document).on('click','.delete-item',function(){
		var id = $(this).attr('data-item');
		var button = $(this);
		
		$.ajax({
			url:'/booking/delete_selection/',
			data:{
				'id':id,
			},
			dataType:'json',
			beforeSend:function(){
				button.text('...');
			},
			success:function(res){
				$(".selection-list").html(res.data);

                if (res.total_selected_items < 1) {
                    Swal.fire({
                        icon: 'warning',
                        title: gettext('No Selections Yet...'),
                        text: gettext("Add some selection to continue to cart...")
                    }).then((result) => {
                        window.location.href = "/"
                      });

                    
                }
			}
		});
	}); 

    $(document).on('change', '#noti-status', function(){
        const query = $(this).val()
        
        $.ajax({
            url:"/dashboard/notification_filter/",
            beforeSend: function(){
                // Removed console.log for "Sending Data..." status
            },
            data: {
                "query": query
            },
            success: function(res){
                // Removed console.log for res.data debugging
				$(".noti-div-main").html(res.data);

            }
        })
    })

    // Mark Notification As Seen
    $(document).on('click', '.mark-noti-as-seen', function(){
        let button = $(this)
        let id = button.attr("data-index")
        // Removed console.log for id debugging
        $.ajax({
            url:"/dashboard/notification_mark_as_seen/",
            beforeSend: function(){
                // Removed console.log for "Sending Data..." status
            },
            data: {
                "id": id
            },
            success: function(res){
                $(".noti-div-"+id).addClass("d-none")
                const Toast = Swal.mixin({
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 1000,
                    timerProgressBar: true,
                })
                    
                Toast.fire({
                    icon: 'success',
                    title: gettext('Notification Seen!')
                })
            }
        })
    })

    // Add to bookmark
    $(document).on('click', '#add-to-bookmark', function(){
        let button = $(this)
        let id = button.attr("data-hotel")
        // Removed console.log for id debugging

        $.ajax({
            url:"/dashboard/add_to_bookmark/",
            beforeSend: function(){
                button.html('<i class="fas fa-spinner fa-spin" style="color: gray;"></i>')
            },
            data: {
                "id": id
            },
            success: function(res){
                $(".noti-div-"+id).addClass("d-none")
                const Toast = Swal.mixin({
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 1000,
                    timerProgressBar: true,
                })
                    
                Toast.fire({
                    icon: res.icon,
                    title: res.data
                })

                if (res.data == gettext("Bookmark Deleted")) {
                    button.html('')
                } else {
                    button.html('')
                }

                if (res.data == gettext("Login To Bookmark Hotel")) {
                    button.html('')
                } 
            }
        })
    })

    // Add Review and Rating
    $(document).on('click', '#review-btn', function(){
        let button = $(this)
        let id = button.attr("data-hotel")
        let review = $("#review-input").val()
        let rating = $("#rating-input").val()
        // Removed console.log for rating debugging

        $.ajax({
            url:"/dashboard/add_review/",
            beforeSend: function(){
                button.html('<i class="fas fa-spinner fa-spin" style="color: white;"></i>')
            },
            data: {
                "id": id,
                "review": review,
                "rating": rating,
            },
            success: function(res){
                const Toast = Swal.mixin({
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 1000,
                    timerProgressBar: true,
                })
                    
                Toast.fire({
                    icon: res.icon,
                    title: res.data
                })

                $("#add-review-button").hide()
                $("#review_div").html(gettext('Review submitted successfully') + ' <i class="fas fa-check-circle"></i> ')
                
            }
        })
    })
})

