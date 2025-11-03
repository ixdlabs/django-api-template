importScripts("https://www.gstatic.com/firebasejs/12.0.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/12.0.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "{{ apiKey }}",
  authDomain: "{{ authDomain }}",
  projectId: "{{ projectId }}",
  storageBucket: "{{ storageBucket }}",
  messagingSenderId: "{{ messagingSenderId }}",
  appId: "{{ appId }}",
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function (payload) {
  console.log("[firebase-messaging-sw.js] Received background message", payload);

  const { title, body } = payload.notification || {
    title: "FCM Background",
    body: "You have a new message",
  };

  self.registration.showNotification(title, { body });
});

self.addEventListener("push", function (event) {
  console.log("[SW] Push event triggered:", event);

  const payload = event.data?.json?.() || {};
  const title = payload.notification?.title || "Push Default";
  const body = payload.notification?.body || "Push Body";

  event.waitUntil(
    self.registration.showNotification(title, {
      body,
      icon: "/static/favicon.ico",
    })
  );
});
