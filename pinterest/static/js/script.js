// like and unlike click button
    $(".like, .unlike").click(function (event) {
        /*THIS AJAX CALL FOR LIKE AND UNLIKE PIN*/

        event.preventDefault();

        var id = this.id;   // Getting Button id

        var post_id1 = id;  //


        // AJAX Request
        $.ajax({
            type: 'POST',
            url: "/pin/" + id + "/like",
            data: {
                'post_id': post_id1
            },
            success: function (data) {

                var like = data['like'];
                var like_value = data['like_value'];

                if (like) {
                    tag = "<i class=\"fa-solid fa-heart\">" + " " + like_value + "</i>"
                } else {
                    tag = "<i class=\"fa-regular fa-heart\">" + " " + like_value + "</i>"
                }
                $("#" + post_id1).html(tag);


            },
            error: function (textStatus, errorThrown) {
                console.log(textStatus);
            }

        })
    });


// follow and unfollow click button
    $(".follow, .unfollow").click(function (event) {

        event.preventDefault();
        var user_id = this.id;   // Getting Button id

        // AJAX Request
        $.ajax({
            type: 'POST',
            url: "/user/follow/" + user_id,
            data: {
                'user_id': user_id
            },
            success: function (data) {

                var follower = data['follower'];
                var follower_count = data['follower_count'];

                if (follower) {
                    tag = "<p style='margin : 0px'>Unfollow</p>"
                    count = follower_count
                } else {
                    tag = "<p style='margin : 0px'>Follow</p>"
                    count = follower_count
                }
                $("#" + user_id).html(tag);
                $("#follower-count").html(count)


            },
            error: function (textStatus, errorThrown) {
                console.log(textStatus);
            }

        })
    });


