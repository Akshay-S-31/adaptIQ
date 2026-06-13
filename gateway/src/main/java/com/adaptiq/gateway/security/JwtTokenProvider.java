package com.adaptiq.gateway.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.auth0.jwt.interfaces.JWTVerifier;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.Date;
import java.util.List;

import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

@Component
public class JwtTokenProvider {

    private final String secretKey = "adaptiq-super-secret-key-for-development";
    private final long validityInMilliseconds = 3600000 * 8L; // 8 hours
    private final Algorithm algorithm = Algorithm.HMAC256(secretKey);

    /**
     * Creates a signed JWT embedding the user's ID, email, role, and employeeId.
     * Role is embedded server-side — clients CANNOT set their own role.
     */
    public String createToken(String userId, String email, String role, String employeeId) {
        Date now = new Date();
        Date validity = new Date(now.getTime() + validityInMilliseconds);

        return JWT.create()
                .withSubject(userId)
                .withClaim("email", email)
                .withClaim("role", role)
                .withClaim("employeeId", employeeId)
                .withIssuedAt(now)
                .withExpiresAt(validity)
                .sign(algorithm);
    }

    public boolean validateToken(String token) {
        try {
            JWTVerifier verifier = JWT.require(algorithm).build();
            verifier.verify(token);
            return true;
        } catch (JWTVerificationException exception) {
            return false;
        }
    }

    /**
     * Extracts the user's role from the JWT and maps it to a Spring Security authority.
     * MANAGER role gets ROLE_MANAGER authority; everyone else gets ROLE_USER.
     */
    public Authentication getAuthentication(String token) {
        DecodedJWT decodedJWT = JWT.decode(token);
        String userId = decodedJWT.getSubject();
        String role = decodedJWT.getClaim("role").asString();

        String authority = "MANAGER".equals(role) ? "ROLE_MANAGER" : "ROLE_USER";
        List<GrantedAuthority> authorities = Collections.singletonList(
                new SimpleGrantedAuthority(authority)
        );

        return new UsernamePasswordAuthenticationToken(userId, token, authorities);
    }

    public String resolveToken(jakarta.servlet.http.HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }

    /** Extract role claim from a token (without full auth pipeline). */
    public String extractRole(String token) {
        return JWT.decode(token).getClaim("role").asString();
    }

    /** Extract employeeId claim from a token. */
    public String extractEmployeeId(String token) {
        return JWT.decode(token).getClaim("employeeId").asString();
    }
}
