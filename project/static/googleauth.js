
const firebaseConfig = {
    apiKey: "AIzaSyDk7B6wLTh6yxRUcxoN2SmoI64ANUTBaeY",
    authDomain: "scheduled-5b0e3.firebaseapp.com",
    databaseURL: "https://scheduled-5b0e3-default-rtdb.firebaseio.com",
    projectId: "scheduled-5b0e3",
    storageBucket: "scheduled-5b0e3.firebasestorage.app",
    messagingSenderId: "384090122282",
    appId: "1:384090122282:web:cd754ea0539bdf246cfb53",
    measurementId: "G-1M901DBRZ3"
  };

const app = firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

function googleSignIn() {
  const provider = new firebase.auth.GoogleAuthProvider();
  auth.signInWithPopup(provider)
      .then((result) => {
          const user = result.user;
          fetch('/login_with_google', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ uid: user.uid, email: user.email })
          })
          .then(response => {
              if (response.ok) {
                  window.location.href = '/schedule';
              }
          });
      })
      .catch((error) => {
          console.error("Error during Google Sign-In:", error);
      });
}