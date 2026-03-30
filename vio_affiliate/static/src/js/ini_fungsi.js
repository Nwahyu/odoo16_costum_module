odoo.define('vio_affiliate.ini_fungsi', function (require) {
    "use strict";

    const core = require('web.core');
    const ajax = require('web.ajax');
    const _t = core._t;
    const publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var session = require('web.session');




    // function modal_hide() {
    //     var modal = document.getElementById('modal-target');
    //     modal.classList.add('hidden');
    // }


    $(document).ready(function () {
        $('.toFormsatu').click(function () {
            document.getElementById("form-satu").scrollIntoView({
                block: 'start',
                behavior: 'smooth',
                inline: 'center'
            });
        });

        function applySelect2() {
            self.$('select.form-control').select2();
            };
         applySelect2();

        $('.toFormdua').click(function () {
            document.getElementById("form-dua").scrollIntoView({
                block: 'start',
                behavior: 'smooth',
                inline: 'center'
            });
        });



        // $('.modal_show').click(function () {
        //     var modal = document.getElementById('modal-target');
        //     modal.classList.remove('hidden');
        // });
    
    
        // $('.modal_hide').click(function () {
        //     var modal = document.getElementById('modal-target');
        //     modal.classList.add('hidden');
        // });


        // btn get code aff di home aff (/my/affiliate)
        $("#btn-get-code").click(function () {
            $("#usr_aff_code").select();
            $(this).text('Copied')
            setTimeout(function () {
                $("#btn-get-code").html("<i class='fa fa-copy' />&nbsp;Copy");
                window.getSelection().removeAllRanges();
                $("#usr_aff_code").blur();
            }, 2000);
            document.execCommand('copy');
            return false;
        });

        // btn get link aff di home aff (/my/affiliate)
        $("#btn-get-url").click(function () {
            $("#usr_aff_url").select();
            $(this).text('Copied')
            setTimeout(function () {
                $("#btn-get-url").html("<i class='fa fa-copy' />&nbsp;Copy");
                window.getSelection().removeAllRanges();
                $("#usr_aff_url").blur();
            }, 2000);
            document.execCommand('copy');
            return false;
        });

        // pop up di form data diri
        if (document.getElementById("input_nama_bank") != null) {
            var nik = document.getElementById("input_nik").value;
            var nama = document.getElementById("input_nama_bank").value;
            var nama_bank = document.getElementById("input_nama_bank").value;
            var no_rek = document.getElementById("input_no_rek").value;
            var nama_rek = document.getElementById("input_nama_rek").value;
            if (!nik || !nama || !nama_bank || !no_rek || !nama_rek) {
                alert("Mohon isi nik, nama, nama bank, nomor rekening, nama rekening.");
            }
        }
    });

    // console.log(session['user_id'])
    if (session['user_id']) {
        // console.log("jalannnnn cooooyyyyy")
        console.log('__     _____ ___           \r\n\\ \\   \/ \/_ _\/ _ \\          \r\n \\ \\ \/ \/ | | | | |         \r\n  \\ V \/  | | |_| |         \r\n _ \\_\/_ |___\\___\/ __  __   \r\n\/ | || |  \/ _ \\  |  \\\/  |  \r\n| | || |_| | | | | |\\\/| |  \r\n| |__   _| |_| | | |  | |  \r\n|_|  |_|  \\___\/  |_| _|_|_ \r\n| |__ (_)___  __ _  | | | |\r\n| \'_ \\| \/ __|\/ _` | | | | |\r\n| |_) | \\__ \\ (_| | |_|_|_|\r\n|_.__\/|_|___\/\\__,_| (_|_|_)');
        session.rpc('/web/session/get_session_info', {}).then(function (result) {
            var userId = result.uid;

            rpc.query({
                model: 'res.users',
                method: 'search_read',
                domain: [['id', '=', userId]],
                fields: ['partner_id'],
            })
            .then(function (user) {
                rpc.query({
                    model: 'res.partner',
                    method: 'search_read',
                    domain: [['id', '=', user[0].partner_id[0]]],
                    fields: ['nik', 'nama_bank', 'no_rek', 'nama_rek']
                })
                .then(function(partner) {
                    if (partner[0].nama_bank == '' || partner[0].no_rek == '' || partner[0].nama_rek == '' || partner[0].nama_bank.length < 3) {
                        console.log('harunsya mucnicl modal bankllll');
                        $('#modalBank').modal('show');
                        // const modalEl = document.getElementById('modalBank');           // grab the modal node
                        // const modal    = bootstrap.Modal.getOrCreateInstance(modalEl); // reuse if already created
                        // modal.show();
                    }
                })
            })
        });
    };
});