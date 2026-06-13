package com.adaptiq.gateway.controller;

import com.adaptiq.gateway.entity.User;
import com.adaptiq.gateway.repository.UserRepository;
import com.adaptiq.gateway.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.Set;

/**
 * Handles user registration and authentication for the AdaptIQ Enterprise Learning Platform.
 *
 * POST /api/v1/auth/register — creates a new user account with role (LEARNER or MANAGER)
 * POST /api/v1/auth/login    — validates credentials and returns a JWT with role embedded
 *
 * Role is validated server-side. Clients cannot forge their role.
 * Supported roles: LEARNER (default), MANAGER
 */
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {

    private final UserRepository userRepository;
    private final JwtTokenProvider jwtTokenProvider;
    private final PasswordEncoder passwordEncoder;

    private static final Set<String> VALID_ROLES = Set.of("LEARNER", "MANAGER");

    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String password = request.get("password");
        String fullName = request.getOrDefault("fullName", "");
        String roleInput = request.getOrDefault("role", "LEARNER").toUpperCase();
        String employeeId = request.getOrDefault("employeeId", "EMP-1001");

        if (email == null || email.isBlank() || password == null) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Email and password are required."));
        }

        // Enforce strong password: at least 8 characters, 1 uppercase, 1 number, 1 special character
        String passwordRegex = "^(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&#])[A-Za-z\\d@$!%*?&#]{8,}$";
        if (!password.matches(passwordRegex)) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Password must be at least 8 characters long, contain one uppercase letter, one number, and one special character."));
        }

        // Server-side role validation — only known roles accepted
        if (!VALID_ROLES.contains(roleInput)) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Invalid role. Accepted values: LEARNER, MANAGER"));
        }

        if (userRepository.findByEmail(email).isPresent()) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(Map.of("error", "An account with this email already exists."));
        }

        User user = User.builder()
                .email(email.toLowerCase().trim())
                .passwordHash(passwordEncoder.encode(password))
                .fullName(fullName.trim())
                .role(roleInput)
                .employeeId(employeeId)
                .build();
        user = userRepository.save(user);

        log.info("Registered new user [{}] role={} email={}", user.getId(), user.getRole(), user.getEmail());

        String token = jwtTokenProvider.createToken(
                user.getId().toString(), user.getEmail(), user.getRole(), user.getEmployeeId());

        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "token", token,
                "user", Map.of(
                        "id", user.getId().toString(),
                        "email", user.getEmail(),
                        "fullName", user.getFullName() != null ? user.getFullName() : "",
                        "role", user.getRole(),
                        "employeeId", user.getEmployeeId()
                )
        ));
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String password = request.get("password");

        if (email == null || password == null) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Email and password are required."));
        }

        User user = userRepository.findByEmail(email.toLowerCase().trim()).orElse(null);

        if (user == null || !passwordEncoder.matches(password, user.getPasswordHash())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid email or password."));
        }

        String token = jwtTokenProvider.createToken(
                user.getId().toString(), user.getEmail(), user.getRole(), user.getEmployeeId());

        log.info("User [{}] role={} logged in", user.getId(), user.getRole());

        return ResponseEntity.ok(Map.of(
                "token", token,
                "user", Map.of(
                        "id", user.getId().toString(),
                        "email", user.getEmail(),
                        "fullName", user.getFullName() != null ? user.getFullName() : "",
                        "role", user.getRole(),
                        "employeeId", user.getEmployeeId()
                )
        ));
    }
}

